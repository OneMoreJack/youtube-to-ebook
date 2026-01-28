# YouTube to Ebook

> Forked from [zarazhangrui/youtube-to-ebook](https://github.com/zarazhangrui/youtube-to-ebook) - 特别致谢！

将 YouTube 视频转换为精美的 EPUB 电子书。支持两种模式：
- **视频转电子书**：指定视频 ID，直接生成电子书（新功能 ✨）
- **频道订阅周刊**：订阅多个频道，自动获取最新视频生成周刊

---

## 🚀 快速开始

### 1. 克隆并安装依赖

```bash
git clone https://github.com/OneMoreJack/youtube-to-ebook.git
cd youtube-to-ebook
pip install -r requirements.txt
```

### 2. 配置 API Keys

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入你的 API Keys：

#### YouTube Data API (免费)

> 仅「功能二：频道订阅周刊」需要，如果只使用视频转电子书功能可跳过此步骤。

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目
3. 启用 "YouTube Data API v3"
4. 创建凭据 → API Key
5. 复制到 `.env` 的 `YOUTUBE_API_KEY`

#### Anthropic Claude API

> [!IMPORTANT]
> **🇨🇳 中国大陆用户获取方式**
> 
> 由于 Anthropic 官方不对中国大陆开放，可通过代理服务获取：
> 
> 1. 访问 https://cc.honoursoft.cn/register?aff=dlK9 （我的邀请链接）
> 2. 注册后获取 API key
> 3. 在 `.env` 中配置：
>    ```
>    ANTHROPIC_BASE_URL=https://cc.honoursoft.cn
>    ANTHROPIC_API_KEY=你的API密钥
>    ```

**官方 API（海外用户）：**
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 创建 API key
3. 在 `.env` 中配置 `ANTHROPIC_API_KEY`
4. **删除** `ANTHROPIC_BASE_URL` 这一行

---

## 🎬 功能一：视频转电子书（新功能）

直接将特定 YouTube 视频转换为 EPUB 电子书。

> [!TIP]
> 此功能**不需要 YouTube Data API**，只需配置 Claude API 即可使用。

### 命令行方式

```bash
# 单个视频
python video_to_ebook.py VIDEO_ID

# 多个视频
python video_to_ebook.py VIDEO_ID_1 VIDEO_ID_2 VIDEO_ID_3

# 支持 URL 格式
python video_to_ebook.py https://www.youtube.com/watch?v=abc123

# 自定义书名
python video_to_ebook.py --title "My Collection" VIDEO_ID_1 VIDEO_ID_2
```

### Web 界面

```bash
python -m streamlit run video_dashboard.py
```

在浏览器中粘贴视频 ID 或 URL，点击生成即可。

> 📂 生成的电子书保存在项目目录的 `ebooks/` 文件夹中，不会发送邮件。

---

## 📺 功能二：频道订阅周刊（原功能）

订阅你喜欢的 YouTube 频道，自动获取最新视频并生成周刊。

### 配置订阅频道

编辑 `channels.txt`，每行一个频道 handle：

```
@mkbhd
@veritasium
@3blue1brown
```

### 生成周刊

```bash
python main.py
```

### 可选：Web Dashboard

```bash
python -m streamlit run dashboard.py
```

### 可选：邮件发送

在 `.env` 中配置 Gmail：

```
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
```

App Password 获取：https://myaccount.google.com/apppasswords

---

## 🛠 进阶配置

### Mac 自动化

每周自动运行：

```bash
# 复制 plist 到 LaunchAgents
cp com.youtube.newsletter.plist ~/Library/LaunchAgents/

# 加载
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.youtube.newsletter.plist
```

### 故障排除

**"ModuleNotFoundError" 错误**

Mac 可能有多个 Python 版本，需要确认正确的路径：

```bash
which python3
# 用返回的完整路径替换脚本中的 python3
```

---

## 📁 项目结构

```
├── video_to_ebook.py    # 视频转电子书（新功能）
├── video_dashboard.py   # 视频转电子书 Web UI（新功能）
├── main.py              # 频道订阅周刊入口
├── dashboard.py         # 频道订阅 Web UI
├── get_videos.py        # 获取频道最新视频
├── get_transcripts.py   # 提取视频字幕
├── write_articles.py    # Claude AI 生成文章
├── create_ebook.py      # 生成 EPUB
├── send_email.py        # 邮件发送
├── channels.txt         # 订阅频道列表
├── .env                 # API Keys（不提交）
└── ebooks/              # 生成的电子书
```

## 🐛 已知问题

| 问题 | 解决方案 |
|------|---------|
| Shorts 无法通过时长过滤 | 检查 `/shorts/` URL |
| 搜索 API 顺序不对 | 使用 uploads playlist |
| 字幕 API 语法变更 | 使用 `ytt_api.fetch()` |
| 云服务器被封禁 | 本地运行，不要用 GitHub Actions |
| 字幕中人名拼写错误 | 将视频描述传给 Claude |
| 文章被截断 | 增加 `max_tokens` |

## License

MIT

---

Built with Claude AI
