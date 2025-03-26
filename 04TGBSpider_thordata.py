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


# ========== 获取博客列表 ==========
def get_blog_list(page):
    url = f"http://www.tgb.cn/blog/2166241?page={page}"
    try:
        res = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        res.raise_for_status()
        print(f"\n[DEBUG] 第 {page} 页 HTML 前 1000 字：\n")
        print(res.text[:1000])  # 打印前1000字符
    except Exception as e:
        print(f"[请求失败] 第 {page} 页 -> {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    blog_items = soup.select(".blog-list .blog-item")
    print(f"[DEBUG] blog_items 抓取数量: {len(blog_items)}")

    blogs = []
    for item in blog_items:
        a_tag = item.select_one("a")
        href = a_tag["href"]
        title = a_tag.text.strip()
        blog_id = href.split("/")[-1]
        full_url = "https://www.tgb.cn" + href
        blogs.append({"id": blog_id, "title": title, "url": full_url})
    return blogs



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

        save2DB_blog(blog["id"], blog["title"], pub_time, content, views, comments)

        # 评论处理（静态页面中已有）
        comment_tags = soup.select(".comment-list .comment-item")
        reply_id = 1
        for comment_tag in comment_tags:
            comment_text = comment_tag.text.strip()
            save2DB_comment(blog["id"], reply_id, comment_text)
            reply_id += 1

        print(f"✅ 成功抓取博客 {blog['id']} - {blog['title']}")

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


# ========== 主逻辑 ==========
def run():
    page = 1
    while True:
        print(f"🔄 正在抓取第 {page} 页...")
        blogs = get_blog_list(page)
        if not blogs:
            print("✅ 全部抓取完毕！")
            break
        for blog in blogs:
            parse_blog(blog)
            time.sleep(random.uniform(1, 2))  # 防反爬
        page += 1


if __name__ == "__main__":
    run()
