import requests
from bs4 import BeautifulSoup
import random
import time
import datetime
import MySqlConnect
import threading
import os

# ========== 1. 读取代理列表 ==========
def get_random_proxy():
    if not os.path.exists('ip.txt'):
        return None
    with open('ip.txt', 'r') as f:
        proxies = f.read().strip().split('\n')
    if proxies:
        proxy = random.choice(proxies)
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    return None

# ========== 2. 请求网页 ==========
def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    proxy = get_random_proxy()
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"[{response.status_code}] 请求失败: {url}")
    except Exception as e:
        print(f"[请求错误] {url} -> {e}")
    return None

# ========== 3. 解析博客列表页面 ==========
def parse_blog_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    posts = []
    items = soup.select('.blog-list .blog-item a')
    for a in items:
        link = a['href']
        blog_id = link.split('/')[-1]
        title = a.text.strip()
        posts.append({
            'id': blog_id,
            'title': title,
            'url': f'https://www.tgb.cn{link}'
        })
    return posts

# ========== 4. 解析单篇博客内容与评论 ==========
def parse_blog_detail(blog):
    html = get_html(blog['url'])
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    content_div = soup.select_one('.blog-content')
    title = blog['title']
    post_id = blog['id']
    time_span = soup.select_one('.blog-info span')
    time_text = time_span.text.strip() if time_span else ''
    content = content_div.text.strip() if content_div else ''

    # 保存文章内容
    save_blog(post_id, title, time_text, content)

    # 评论抓取（如果评论是动态加载的，这里需要后续扩展 Ajax 抓取）
    comment_list = soup.select('.comment-item .comment-text')
    replyid = 1
    for c in comment_list:
        comment = c.text.strip()
        save_comment(post_id, replyid, comment)
        replyid += 1

# ========== 5. 保存到数据库 ==========
def save_blog(blog_id, title, time_text, content):
    sql = f"""
        INSERT INTO tgb_blog (id, title, time, content)
        VALUES ("{blog_id}", "{title}", "{time_text}:00", "{content}")
    """
    MySqlConnect.edit(sql)

def save_comment(postid, replyid, comment):
    sql = f"""
        INSERT INTO tgb_comment (postid, replyid, comment)
        VALUES ("{postid}", "{replyid}", "{comment}")
    """
    MySqlConnect.edit(sql)

# ========== 6. 主流程 ==========
def crawl_tgb():
    page = 1
    while True:
        print(f"正在抓取第 {page} 页...")
        url = f"https://www.tgb.cn/blog/2166241?page={page}"
        html = get_html(url)
        if not html:
            break
        posts = parse_blog_list(html)
        if not posts:
            break

        threads = []
        for post in posts:
            t = threading.Thread(target=parse_blog_detail, args=(post,))
            t.start()
            threads.append(t)
            time.sleep(random.uniform(1, 2))

        for t in threads:
            t.join()

        page += 1
        time.sleep(random.uniform(3, 5))

if __name__ == '__main__':
    crawl_tgb()
