from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random
import datetime
import MySqlConnect
from webdriver_manager.chrome import ChromeDriverManager


def create_driver():
    options = Options()
    options.add_argument("--start-maximized")

    # ✅ 使用一个全新的独立用户数据目录，避免 Chrome 拒绝访问
    options.add_argument("--user-data-dir=" + "/Users/hzs/selenium-chrome-profile")

    # 可选：指定 profile 名（Default 或新建的）
    options.add_argument("--profile-directory=Default")

    # ✅ 初始化 ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver




# ========== 数据库入库 ==========
def save2DB_blog(blog_id, title, pub_time, content, views, comments):
    sql = f"""
    INSERT INTO tgb_blog (
        id, title, time, content, views, comments
    ) VALUES (
        "{blog_id}", "{title}", "{pub_time}", "{content}", "{views}", "{comments}"
    )
    """
    MySqlConnect.edit(sql)

def save2DB_comment(postid, replyid, comment):
    sql = f"""
    INSERT INTO tgb_comment (
        postid, replyid, comment
    ) VALUES (
        "{postid}", "{replyid}", "{comment}"
    )
    """
    MySqlConnect.edit(sql)

# ========== 解析博客正文与评论 ==========
def parse_blog(driver, blog):
    try:
        driver.get(blog["url"])
        time.sleep(2 + random.random())

        soup = BeautifulSoup(driver.page_source, "html.parser")

        content_tag = soup.select_one(".blog-content")
        content = content_tag.text.strip() if content_tag else ""

        time_tag = soup.select_one(".blog-date")
        pub_time = time_tag.text.strip() if time_tag else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        views = int(soup.select_one(".read-num").text.strip()) if soup.select_one(".read-num") else 0
        comments = int(soup.select_one(".comment-num").text.strip()) if soup.select_one(".comment-num") else 0

        title_tag = soup.select_one(".blog-title")
        title = title_tag.text.strip() if title_tag else blog["title"]

        save2DB_blog(blog["id"], title, pub_time, content, views, comments)

        comment_tags = soup.select(".comment-list .comment-item")
        reply_id = 1
        for tag in comment_tags:
            comment_text = tag.text.strip()
            save2DB_comment(blog["id"], reply_id, comment_text)
            reply_id += 1

        print(f"✅ 抓取成功：{blog['id']} - {title}")
        # driver.save_screenshot(f"screenshot_{blog['id']}.png")  # 可选截图保存

    except Exception as e:
        print(f"[❌ 抓取失败] {blog['url']} -> {e}")

# ========== 主流程 ==========
def run():
    driver = create_driver()
    print("🔐 请在打开的浏览器窗口中完成登录后按回车...")
    driver.get("https://www.tgb.cn/login")
    input("✅ 登录完成后请按回车继续...")

    with open("blog_links.txt", "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    for link in links:
        print(f"🔍 正在抓取：{link}")
        blog_id = link.split("/")[-1]
        blog = {"id": blog_id, "title": "N/A", "url": link}
        parse_blog(driver, blog)
        time.sleep(random.uniform(1, 2))

    driver.quit()
    print("✅ 所有链接抓取完毕！")

if __name__ == "__main__":
    run()
