# 🌍 AI-Powered Financial News & Research Bot
**AI 智能金融情报推送机器人 (DeepSeek + DingTalk)**

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-green.svg)](https://platform.deepseek.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **自动化情报系统**：实时监控金融时报 (FT)、福布斯 (Forbes) 及谷歌学术，利用 DeepSeek AI 深度总结核心内容。  
> **Automated Intel System**: Monitors FT, Forbes, and Google Scholar in real-time, leveraging DeepSeek AI for deep summarization.

[English Version Below](#english-version)

---

## 🇨🇳 中文说明 (Chinese Version)

### 📌 项目简介
这是一个专为金融分析和内部控制设计的轻量级自动化系统。它能够每天定时执行以下任务：
1.  **多源抓取**：自动抓取 **Financial Times** 和 **Forbes** 的最新财经报道。
2.  **学术追踪**：通过 **Jina Reader** 穿透谷歌学术，追踪“财务舞弊”与“内部控制”领域的最新研究。
3.  **AI 深度总结**：调用 **DeepSeek AI** 阅读全文，提炼核心结论与详细要点，拒绝碎片化信息。
4.  **精准推送**：通过钉钉机器人实时推送到您的手机，支持关键词过滤。

### 🚀 快速部署指南

只需 5 分钟，无需服务器，即可完成部署：

#### 1. 获取密钥 (Secrets)
* **钉钉 Webhook**：在钉钉群添加“自定义机器人”，安全设置勾选“自定义关键词”，填入 `新闻`。复制得到的 `Webhook URL`。
* **DeepSeek Key**：在 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取以 `sk-` 开头的 API Key。

#### 2. 复制项目 (Fork)
* 点击本项目右上角的 **`Fork`**，将其复制到您的 GitHub 账号下。

#### 3. 配置环境变量 (Secrets)
* 进入您 Fork 后的仓库 -> **`Settings`** -> **`Secrets and variables`** -> **`Actions`**。
* 点击 **`New repository secret`**，添加以下两个变量：
    * `DINGTALK_WEBHOOK`: 粘贴您的钉钉 Webhook 链接。
    * `DEEPSEEK_API_KEY`: 粘贴您的 DeepSeek API 密钥。

#### 4. 激活运行
* 点击仓库顶部的 **`Actions`**，选择 **`I understand my workflows, go ahead and enable them`**。
* 在左侧选中 **`News Push Bot`**，点击右侧 **`Run workflow`** 手动测试。
* 默认每天北京时间 **08:00** 自动推送。

### 🛠️ 如何自定义修改？
如果您需要修改新闻来源或关键词，请直接编辑 `main.py`：

* **修改来源**：编辑第 15 行的 `NEWS_SOURCES`。
* **修改关键词**：编辑第 21 行的 `TARGET_KEYWORDS`（支持中英文）。

---

<a name="english-version"></a>

## 🇬🇧 English Version

### 📌 Introduction
A lightweight automation system designed for financial analysis and internal control.
1.  **Multi-source Fetching**: Scrapes latest financial news from **Financial Times** and **Forbes**.
2.  **Academic Tracking**: Uses **Jina Reader** to track the latest research in "Financial Fraud" and "Internal Control" via Google Scholar.
3.  **Deep AI Summarization**: Powers by **DeepSeek AI** to read full articles and extract core conclusions.
4.  **Smart Push**: Real-time delivery to **DingTalk** with keyword-based filtering.

### 🚀 Quick Start Guide

#### Step 1: Get Your Keys
* **DingTalk Webhook**: Create a "Custom Bot" in DingTalk. Set the security keyword to `新闻`. Copy the `Webhook URL`.
* **DeepSeek API Key**: Obtain your key from [DeepSeek Platform](https://platform.deepseek.com/).

#### Step 2: Fork the Repo
* Click the **`Fork`** button at the top right of this page.

#### Step 3: Configure Secrets
* Go to your repo **`Settings`** -> **`Secrets and variables`** -> **`Actions`**.
* Click **`New repository secret`** to add:
    * `DINGTALK_WEBHOOK`: Your Webhook URL.
    * `DEEPSEEK_API_KEY`: Your DeepSeek API Key.

#### Step 4: Run
* Go to **`Actions`** tab, click **`I understand my workflows...`**.
* Select **`News Push Bot`** and click **`Run workflow`** for a manual test.
* The bot runs automatically at **00:00 UTC** daily.

### 🛠️ Customization
Edit `main.py` directly to customize:
* **RSS Sources**: Modify `NEWS_SOURCES` (around line 15).
* **Keywords**: Modify `TARGET_KEYWORDS` (around line 21).

---
[回到顶部 / Back to Top](#ai-powered-financial-news--research-bot)
