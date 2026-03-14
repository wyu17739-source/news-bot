import feedparser
import requests
import json
import os
from openai import OpenAI

# 获取环境变量
DINGTALK_WEBHOOK = os.environ.get("DINGTALK_WEBHOOK")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# 初始化 AI 客户端
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

NEWS_SOURCES = {
    "Bloomberg 市场": "https://feeds.bloomberg.com/markets/news.rss",
    "CNN 头条": "http://rss.cnn.com/rss/edition.rss"
}

# 👉 你关心的商业新闻关键词列表
TARGET_KEYWORDS = ["期货", "商品", "大宗", "原油", "黄金", "美联储", "降息", "oil", "gold", "commodity", "futures"]

def is_target_news(text):
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in TARGET_KEYWORDS)

def get_full_text(url):
    """利用 Jina 抓取网页纯文本正文"""
    try:
        jina_url = f"https://r.jina.ai/{url}"
        response = requests.get(jina_url, timeout=20)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"网页抓取失败: {e}")
    return ""

def ai_summarize_news(full_text):
    """AI 处理商业新闻"""
    if not full_text or len(full_text) < 100:
        return "网页内容过短或抓取失败，无法进行 AI 总结。"
        
    content = full_text[:8000] 
    prompt = f"""
    你是一个专业的金融分析师。请阅读以下这篇新闻的正文，并输出中文总结。
    
    格式要求：
    **🎯 核心结论**：（一句话概括核心信息）
    **📝 详细提炼**：
    - （要点1：需包含具体数据或事件事实）
    - （要点2...）
    
    新闻正文：
    {content}
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return "AI 新闻总结出错。"

def fetch_scholar_research():
    """抓取并总结谷歌学术最新研究"""
    # 搜索词为“财务舞弊 内部控制”，scisbd=1 表示按最新日期排序
    scholar_url = "https://scholar.google.com/scholar?q=%E8%B4%A2%E5%8A%A1%E8%88%9E%E5%BC%8A+%E5%86%85%E9%83%A8%E6%8E%A7%E5%88%B6&scisbd=1"
    
    try:
        print("正在抓取谷歌学术...")
        jina_url = f"https://r.jina.ai/{scholar_url}"
        response = requests.get(jina_url, timeout=20)
        
        if response.status_code == 200:
            content = response.text[:8000]
            
            prompt = f"""
            你是一个专业的学术研究助手。以下是谷歌学术关于“财务舞弊”与“内部控制”最新论文的搜索结果。
            请根据提取到的摘要片段，为我输出一份学术简报。
            
            格式要求：
            **🎓 学术界最新研究焦点**：（用一两句话概括最近学者们主要在研究该领域的什么具体问题）
            **📚 核心论文追踪**：
            - **《[提炼出的论文标题]》**：[作者/年份] —— [根据片段总结其研究发现或思路]
            - （列出2-3篇最有价值的即可）
            
            搜索结果正文：
            {content}
            """
            
            res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return f"#### 🎓 谷歌学术跟踪 (财务舞弊 & 内部控制)\n> {res.choices[0].message.content}\n\n---\n"
    except Exception as e:
        print(f"学术抓取失败: {e}")
    return "#### 🎓 谷歌学术跟踪\n> 暂无最新学术数据或抓取受限。\n\n---\n"

def send_dingtalk(text):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "综合情报简报", 
            "text": text
        }
    }
    requests.post(DINGTALK_WEBHOOK, data=json.dumps(data), headers=headers)

def fetch_news():
    # 注意：包含了钉钉安全关键词“新闻”
    final_message = "### 🌍 综合情报与新闻简报\n\n"
    
    # ---------------- 1. 处理谷歌学术模块 ----------------
    scholar_report = fetch_scholar_research()
    final_message += scholar_report
    
    # ---------------- 2. 处理商业新闻模块 ----------------
    has_news = False
    for name, rss_url in NEWS_SOURCES.items():
        feed = feedparser.parse(rss_url)
        source_message = f"#### 📢 {name}\n"
        source_has_news = False
        
        for entry in feed.entries[:8]:
            title = entry.title
            summary = getattr(entry, 'summary', '')
            link = entry.link
            
            if not is_target_news(title + " " + summary):
                continue
                
            print(f"命中新闻关键词，正在分析: {title}")
            source_has_news = True
            has_news = True
            
            full_article = get_full_text(link)
            ai_report = ai_summarize_news(full_article)
            
            source_message += f"**原文**: [{title}]({link})\n"
            source_message += f"> {ai_report}\n\n"
            
        if source_has_news:
            final_message += source_message
            
    # 如果今天有学术更新或命中了新闻，就推送
    if has_news or "核心论文追踪" in scholar_report:
        send_dingtalk(final_message)
    else:
        print("今日无符合条件的情报。")

if __name__ == "__main__":
    fetch_news()
