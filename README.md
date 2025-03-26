# Taoguba Blog Crawler

一个基于 Python、Playwright 和 Selenium 的多线程淘股吧博客爬虫项目，支持自动登录、博客目录提取、博文内容保存、图片下载、异常管理和 MySQL 存储等功能。

---

## 📁 项目结构

```
.
├── 00爬免费代理.py               # 旧版 IP 代理爬虫脚本
├── 02TaogubaCrawler.py           # 基础内容 + 评论爬虫（使用 requests 和 BeautifulSoup）
├── 03阿布云版.py                 # 使用阿布云付费代理爬虫
├── 04TGBSpider.py                # 基础爬虫入口（含数据库保存）
├── 04TGBSpider_from_links.py     # 从 blog_links.txt 中提取并爬取博文内容
├── 04TGBSpider_selenium.py       # 使用 Selenium 自动登录并爬取博文（手动交互）
├── 04TGBSpider_thordata.py       # 使用 Thordata 付费代理爬虫脚本
├── blog_links.txt                # 手动整理的博文链接列表
├── blog_links-auto.txt           # 自动提取生成的博文链接
├── extract_blog_links.py         # 基于 Selenium 提取某个目录页的链接
├── error_urls.txt                # 下载失败的链接列表
├── final_state.png               # 登录后截图（调试用）
├── html_template.html            # 模板 HTML 文件
├── ip.txt                        # 代理 IP 列表文件
├── MySqlConnect.py               # MySQL 数据库连接和执行操作模块
├── README.md                     # 项目说明文档
├── tgb_blog_crawler.py           # ✅ 核心：使用 Playwright 批量提取博文目录页所有链接并分类保存
├── tgb_login.py                  # ✅ 自动登录淘股吧并保存 Cookie
├── tgb_cookies.json              # ✅ 登录后保存的 Cookie
├── tgb_post_downloader.py        # ✅ 根据链接下载博文正文 + 图片 + 元信息保存为文件夹
```

---

## ✅ 使用说明

### 1️⃣ 自动登录并保存 Cookie

```bash
python tgb_login.py
```
> 会自动打开浏览器，模拟用户点击、输入账号密码、登录。登录成功后自动保存 cookie 到 `tgb_cookies.json`。

### 2️⃣ 提取用户博客所有分类下的所有博文链接

```bash
python tgb_blog_crawler.py
```
> 会自动加载 cookie，逐个访问目录页，翻页提取所有博文链接，并保存到：
>
> - `blog_links/section_XXXX.txt`：每个分类单独存储
> - `blog_links/all_links.txt`：整合后所有链接 + 标题 + 阅读/评论数 + 日期
> - `blog_links/all_urls.txt`：仅链接列表，供下载正文使用

### 3️⃣ 下载博文正文内容、HTML、图片和元信息

```bash
python tgb_post_downloader.py
```
> 加载 `blog_links/all_urls.txt` 中的链接，逐篇下载：
>
> - `content.html`: 原始正文 HTML
> - `content.txt`: 提取的正文纯文本（含图片链接）
> - `images/`: 所有正文内图片下载保存
> - `metadata.json`: 标题、原始链接、下载时间、图片数

如下载失败，错误链接将记录在 `error_urls.txt` 中。

---

## 🔧 环境依赖

### 📦 Python 依赖

请使用 Python 3.11+ 建议使用虚拟环境：

```bash
pip install -r requirements.txt
```

如无 requirements.txt，可手动安装：
```bash
pip install playwright selenium beautifulsoup4 requests python-dotenv
playwright install
```

### 🧪 Playwright 依赖安装
```bash
playwright install firefox
```

---

## 📌 配置 .env 文件

请在项目根目录下创建 `.env` 文件，写入：

```env
TGB_USERNAME=your_username
TGB_PASSWORD=your_password
```

---

## ✅ 成功运行示例

```
Launching Firefox browser...
Cookies loaded from tgb_cookies.json
Crawling section 41077...
Processing page 1...
Found 50 links on page 1
...
Saved 240 links to blog_links/section_41077.txt
Saved all links to blog_links/all_links.txt
Saved all URLs to blog_links/all_urls.txt
```

---

## 📞 联系方式 / 问题反馈

欢迎提交 Issue 或通过私信交流使用问题与建议。

---

## 📜 License

MIT License

