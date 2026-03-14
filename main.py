import feedparser
import requests
import json
import os
from deep_translator import GoogleTranslator

# 获取你在 GitHub Secrets 填写的钉钉 Webhook
DINGTALK_WEBHOOK = os.environ.get("DINGTALK_WEBHOOK")

# 新闻源 RSS 地址
NEWS_SOURCES = {
    "Bloomberg 市场": "https://feeds.bloomberg.com/markets/news.rss",
    "CNN 头条": "http://rss.cnn.com/rss/edition.rss"
}

def translate_text(text):
    try:
        # 调用免费的谷歌翻译接口，将文本翻译为简体中文
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译出错: {e}")
        return text # 如果翻译失败，为了不丢失信息，原样返回英文

def send_dingtalk(text):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "国际新闻推送", 
            "text": text
        }
    }
    requests.post(DINGTALK_WEBHOOK, data=json.dumps(data), headers=headers)

def fetch_news():
    # 注意：这里的“新闻”两个字是为了触发钉钉机器人的安全关键词
    full_message = "### 🌍 实时新闻推送 (自动翻译版)\n\n"
    
    for name, url in NEWS_SOURCES.items():
        feed = feedparser.parse(url)
        full_message += f"#### 📢 {name}\n"
        
        # 仅获取前 3 条新闻，防止消息太长被钉钉截断
        for entry in feed.entries[:3]:
            original_title = entry.title
            link = entry.link
            
            # 执行翻译
            translated_title = translate_text(original_title)
            
            # 拼接到最终的消息中
            full_message += f"- [{translated_title}]({link})\n"
            # 如果你想同时对照看英文原标题，可以把下面这行代码开头的 # 删掉
            # full_message += f"  > *{original_title}*\n"
            
        full_message += "\n---\n"
    
    send_dingtalk(full_message)

if __name__ == "__main__":
    fetch_news()
