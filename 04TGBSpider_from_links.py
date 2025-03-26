import requests
from bs4 import BeautifulSoup
import time
import random
import datetime
import MySqlConnect

# ========== Thordata 代理配置 ==========
proxy_host = "l49oi8o8.pr.thordata.net"
proxy_port = "9999"
proxy_user = "td-customer-akOrV26oogqg"
proxy_pass = "FTHxjich7eu5"

proxies = {
    "http": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
    "https": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.15; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# ========== 抓取文章正文与评论 ==========
def parse_blog(blog):
    try:
        res = requests.get(blog["url"], headers=headers, proxies=proxies, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

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
        for comment_tag in comment_tags:
            comment_text = comment_tag.text.strip()
            save2DB_comment(blog["id"], reply_id, comment_text)
            reply_id += 1

        print(f"✅ 成功抓取博客 {blog['id']} - {title}")

    except Exception as e:
        print(f"[错误] 抓取失败：{blog['url']} -> {e}")


# ========== 数据入库 ==========
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


# ========== 主逻辑：从 blog_links.txt 抓取 ==========
def run_from_links(file="blog_links.txt"):
    with open(file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    for link in links:
        blog_id = link.strip().split("/")[-1]
        blog = {"id": blog_id, "title": "N/A", "url": link}
        parse_blog(blog)
        time.sleep(random.uniform(1, 2))


if __name__ == "__main__":
    run_from_links()
