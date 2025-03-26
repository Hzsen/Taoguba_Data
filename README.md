# TGB.cn 博主文章+评论爬虫 (04TGBSpider.py)

这是一个专为爬取 [淘股吧博客站 tgb.cn](https://www.tgb.cn/blog/2166241) 博主 "万师虎" 发布的所有博文及其对应评论所编写的 Python 爬虫。

---

## 🧩 功能特性
- 自动抓取指定博主所有博文（自动翻页）
- 支持爬取每篇博客的：
  - 标题
  - 发布时间
  - 正文内容
- 抓取每篇博客下的评论（静态加载部分）
- 使用代理池 `ip.txt`，避免被目标站点封锁 IP
- 数据自动写入 MySQL 数据库（复用 `MySqlConnect.py`）
- 多线程加速抓取，提高效率

---

## 🗂 项目结构

```
├── 00爬免费代理.py       # 抓取西刺代理并验证写入 ip.txt
├── 02TaogubaCrawler.py   # 淘股吧文章+评论爬虫（免费代理版）
├── 03阿布云版.py         # 使用阿布云动态代理的爬虫版本
├── 04TGBSpider.py        # ✅ 本项目主脚本，爬取 tgb.cn 万师虎的博客
├── MySqlConnect.py       # 封装的 MySQL 写入函数
├── ip.txt                # 有效代理 IP 列表（由 00爬免费代理.py 生成）
└── venv/                 # Python 虚拟环境
```

---

## 💻 依赖安装

请使用虚拟环境安装依赖：

```bash
cd your/project/path
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4 pymysql
```

---

## 🗃️ MySQL 数据库配置

请确保你已经在 MySQL 中创建了以下两张表：

```sql
CREATE TABLE tgb_blog (
    id INT PRIMARY KEY,
    title TEXT,
    time DATETIME,
    content TEXT
);

CREATE TABLE tgb_comment (
    postid INT,
    replyid INT,
    comment TEXT
);
```

你需要在 `MySqlConnect.py` 中配置你自己的数据库连接信息。

---

## 🚀 使用方法

```bash
# 进入虚拟环境（如使用）
source venv/bin/activate

# 运行爬虫主程序
python 04TGBSpider.py
```

---

## 🔧 可选配置：使用阿布云动态代理

如你有阿布云账号，也可参考 `03阿布云版.py` 中的写法，将代理替换为商业代理。

---

## 📝 注意事项
- 评论部分仅抓取静态 HTML 部分，若存在 Ajax 评论加载，需额外补充接口抓取逻辑。
- 若运行失败，确认：
  - 代理 IP 是否有效
  - 数据库连接配置是否正确
  - Python 依赖是否安装齐全

---

## 🧠 后续可扩展
- 抓取点赞数 / 浏览量等附加信息
- 支持抓取其他博主文章
- 数据输出为 CSV/JSON 文件
- 日志记录 / 错误重试机制

---

## 📬 作者
如有问题欢迎交流！
