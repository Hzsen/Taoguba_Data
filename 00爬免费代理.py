#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import random

def get_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ]
    return {
        "User-Agent": random.choice(user_agents)
    }

# 测试代理是否可用
def test_proxy(ip_port, test_url="https://httpbin.org/ip"):
    proxies = {
        "http": f"http://{ip_port}",
        "https": f"http://{ip_port}"
    }
    try:
        response = requests.get(test_url, proxies=proxies, headers=get_headers(), timeout=5)
        if response.status_code == 200:
            print(f"[有效] {ip_port}")
            return True
    except:
        pass
    print(f"[无效] {ip_port}")
    return False

# 抓取 89ip.cn 上的代理
def crawl_89ip(pages=3):
    valid_ips = []
    print("开始抓取代理...")
    for page in range(1, pages + 1):
        url = f"https://www.89ip.cn/index_{page}.html"
        try:
            res = requests.get(url, headers=get_headers(), timeout=5)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('table.layui-table tbody tr')
            for row in rows:
                tds = row.find_all('td')
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                ip_port = f"{ip}:{port}"
                if test_proxy(ip_port):
                    valid_ips.append(ip_port)
            time.sleep(random.uniform(1, 3))  # 防止被封
        except Exception as e:
            print(f"[抓取失败] 第 {page} 页: {e}")
    return valid_ips

# 写入文件
def write_to_file(ip_list, path="ip.txt"):
    with open(path, "w", encoding="utf-8") as f:
        for ip in ip_list:
            f.write(ip + "\n")
    print(f"✅ 已保存 {len(ip_list)} 个可用代理到 {path}")

if __name__ == "__main__":
    proxies = crawl_89ip(pages=3)
    write_to_file(proxies)
