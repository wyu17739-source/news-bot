import feedparser
import requests
import json
import os
from deep_translator import GoogleTranslator

DINGTALK_WEBHOOK = os.environ.get("DINGTALK_WEBHOOK")

NEWS_SOURCES = {
    "Bloomberg 市场": "https://feeds.bloomberg.com/markets/news.rss",
    "CNN 头条": "http://rss.cnn.com/rss/edition.rss"
}

def translate_text(text):
    if not text:
        return ""
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译出错: {e}")
        return text 

def get_detailed_summary(url):
    """让程序替你'点开'链接，抓取网页正文并提取核心段落"""
    try:
        # 使用 r.jina.ai 免费服务，它能自动去除网页广告和代码，提取干净的正文
        jina_url = f"https://r.jina.ai/{url}"
        # 设置超时时间，防止个别网页卡死
        response = requests.get(jina_url, timeout=15)
        
        if response.status_code == 200:
            text = response.text
            # 过滤掉网页上的短碎文本（如菜单、作者名），只保留长度大于30个字符的正文段落
            paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 30]
            
            # 新闻的核心通常在前几段，我们将前 3 段拼接起来作为深度摘要
            core_content = " ".join(paragraphs[:3])
            
            # 限制总长度，防止钉钉消息超长导致发送失败
            if len(core_content) > 500:
                core_content = core_content[:500] + "......(受限于篇幅，已折叠)"
                
            return core_content
    except Exception as e:
        print(f"抓取正文失败 ({url}): {e}")
    return ""

def send_dingtalk(text):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "国际新闻深度推送", 
            "text": text
        }
    }
    requests.post(DINGTALK_WEBHOOK, data=json.dumps(data), headers=headers)

def fetch_news():
    full_message = "### 🌍 实时新闻与深度摘要\n\n"
    
    for name, rss_url in NEWS_SOURCES.items():
        feed = feedparser.parse(rss_url)
        full_message += f"#### 📢 {name}\n"
        
        for entry in feed.entries[:3]:
            title = translate_text(entry.title)
            link = entry.link
            
            print(f"正在深度抓取: {title}") # 在 GitHub 日志中方便查看进度
            
            # 1. 自动去目标网页抓取正文的核心段落
            english_summary = get_detailed_summary(link)
            
            # 2. 如果遇上极强的防爬虫导致抓取失败，退回到使用 RSS 自带的简单摘要兜底
            if not english_summary:
                english_summary = getattr(entry, 'summary', '（原网页限制，暂无详细内容）')
                english_summary = english_summary.replace('<p>', '').replace('</p>', '') # 简单清理标签
            
            # 3. 将抓取到的深度内容翻译成中文
            translated_summary = translate_text(english_summary)
            
            full_message += f"- **[{title}]({link})**\n"
            full_message += f"  > 💡 **详细内容**：{translated_summary}\n\n"
            
        full_message += "---\n"
    
    send_dingtalk(full_message)

if __name__ == "__main__":
    fetch_news()
