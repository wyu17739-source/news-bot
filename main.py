import feedparser
import requests
import json
import os
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup # 引入网页清理工具

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

def send_dingtalk(text):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "国际新闻摘要", 
            "text": text
        }
    }
    requests.post(DINGTALK_WEBHOOK, data=json.dumps(data), headers=headers)

def fetch_news():
    # 加入“新闻”二字以通过钉钉关键词校验
    full_message = "### 🌍 实时新闻与摘要推送\n\n"
    
    for name, url in NEWS_SOURCES.items():
        feed = feedparser.parse(url)
        full_message += f"#### 📢 {name}\n"
        
        # 仅获取前 3 条，避免消息过长
        for entry in feed.entries[:3]:
            # 1. 提取并翻译标题
            title = translate_text(entry.title)
            link = entry.link
            
            # 2. 提取新闻摘要 (如果 RSS 源里有的话)
            raw_summary = getattr(entry, 'summary', '')
            # 使用 BeautifulSoup 清理摘要里可能附带的 HTML 标签和图片链接
            clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text().strip()
            
            # 如果摘要太长，截取前200个字符即可
            if len(clean_summary) > 200:
                clean_summary = clean_summary[:200] + "..."
                
            # 翻译摘要
            translated_summary = translate_text(clean_summary) if clean_summary else "（本条暂无摘要说明）"
            
            # 3. 拼接到最终格式里 (加粗标题，并在下方用引用格式放摘要)
            full_message += f"- **[{title}]({link})**\n"
            full_message += f"  > 💡 **摘要**：{translated_summary}\n\n"
            
        full_message += "---\n"
    
    send_dingtalk(full_message)

if __name__ == "__main__":
    fetch_news()
