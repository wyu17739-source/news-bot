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

# 替换为 FT 和 福布斯的 RSS 源
NEWS_SOURCES = {
    "Financial Times (金融时报)": "https://www.ft.com/markets?format=rss",
    "Forbes (福布斯市场)": "https://www.forbes.com/markets/feed/"
}

# 👉 核心监控关键词（涵盖商品、期货、财务舞弊、内控的中英文）
TARGET_KEYWORDS = [
    "期货", "商品", "大宗", "原油", "黄金", "铜", 
    "财务舞弊", "财务造假", "内部控制", "审计",
    "commodity", "futures", "oil", "gold", "copper",
    "fraud", "internal control", "audit", "scandal", "accounting"
]

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
        print(f"网页抓取失败 ({url}): {e}")
    return ""

def ai_summarize_news(full_text):
    """AI 处理商业新闻"""
    if not full_text or len(full_text) < 100:
        return "网页内容过短或抓取受限，无法进行 AI 深度总结。"
        
    content = full_text[:8000] 
    prompt = f"""
    你是一个专业的金融与风控分析师。请阅读以下这篇来自顶级财经媒体的新闻正文，并输出中文总结。
    
    格式要求：
    **🎯 核心结论**：（一句话概括这篇新闻的最核心信息，特别是对商品市场或公司内控的影响）
    **📝 详细提炼**：
    - （要点1：需包含具体数据、公司名称或事件事实）
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
    """双引擎抓取谷歌学术：模块A(商品期货) + 模块B(财务舞弊内控)"""
    
    # 定义两个不同的学术搜索任务 (scisbd=1 表示按最新时间排序)
    scholar_tasks = {
        "📊 模块A：商品与期货市场": "https://scholar.google.com/scholar?q=%E5%95%86%E5%93%81+%E6%9C%9F%E8%B4%A7&scisbd=1",
        "🚨 模块B：财务舞弊与内部控制": "https://scholar.google.com/scholar?q=%E8%B4%A2%E5%8A%A1%E8%88%9E%E5%BC%8A+%E5%86%85%E9%83%A8%E6%8E%A7%E5%88%B6&scisbd=1"
    }
    
    academic_report = ""
    
    for topic, url in scholar_tasks.items():
        try:
            print(f"正在抓取谷歌学术: {topic}")
            jina_url = f"https://r.jina.ai/{url}"
            response = requests.get(jina_url, timeout=20)
            
            if response.status_code == 200:
                content = response.text[:6000]
                
                prompt = f"""
                你是一个专业的学术研究助手。以下是谷歌学术关于特定主题的最新论文搜索结果片段。
                
                格式要求：
                **🎓 {topic} 最新焦点**：（一句话概括当前学者们关注的核心）
                **📚 核心论文追踪**：
                - **《[论文标题]》**：[作者/年份] —— [根据片段总结研究发现或模型]
                - （精选最相关的2篇即可）
                
                搜索结果正文：
                {content}
                """
                
                res = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                academic_report += f"#### {topic}\n> {res.choices[0].message.content}\n\n"
        except Exception as e:
            print(f"学术抓取失败 ({topic}): {e}")
            
    if not academic_report:
        return "#### 🎓 谷歌学术跟踪\n> 暂无最新学术数据或抓取受限。\n\n---\n"
        
    return academic_report + "---\n"

def send_dingtalk(text):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "专业领域情报简报", 
            "text": text
        }
    }
    requests.post(DINGTALK_WEBHOOK, data=json.dumps(data), headers=headers)

def fetch_news():
    # 包含了钉钉安全关键词“新闻”
    final_message = "### 🌍 专属领域情报与新闻简报\n\n"
    
    # ---------------- 1. 处理谷歌学术模块 ----------------
    print("开始执行学术抓取模块...")
    scholar_report = fetch_scholar_research()
    final_message += scholar_report
    
    # ---------------- 2. 处理商业新闻模块 ----------------
    print("开始执行外媒新闻模块...")
    has_news = False
    for name, rss_url in NEWS_SOURCES.items():
        feed = feedparser.parse(rss_url)
        source_message = f"#### 📢 {name}\n"
        source_has_news = False
        
        # 增加遍历数量，以防垂直领域的文章较少
        for entry in feed.entries[:15]:
            title = entry.title
            summary = getattr(entry, 'summary', '')
            link = entry.link
            
            if not is_target_news(title + " " + summary):
                continue
                
            print(f"命中目标，正在由 AI 深度分析: {title}")
            source_has_news = True
            has_news = True
            
            full_article = get_full_text(link)
            ai_report = ai_summarize_news(full_article)
            
            source_message += f"**原文**: [{title}]({link})\n"
            source_message += f"> {ai_report}\n\n"
            
        if source_has_news:
            final_message += source_message
            
    # 推送逻辑判断
    if has_news or "最新焦点" in scholar_report:
        send_dingtalk(final_message)
        print("推送成功！")
    else:
        print("今日无符合条件的情报。")

if __name__ == "__main__":
    fetch_news()
