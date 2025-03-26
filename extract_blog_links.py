from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--user-data-dir=/Users/hzs/selenium-chrome-profile")
    options.add_argument("--profile-directory=Default")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_links(driver, url, output_file):
    print(f"🔍 正在访问：{url}")
    driver.get(url)

    try:
        # ✅ 等待文章列表加载（最多10秒）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".tleftbox a"))
        )
    except Exception as e:
        print(f"[❌ 页面未加载] {e}")
        return

    scroll_to_bottom(driver)
    time.sleep(1)

    link_elements = driver.find_elements(By.CSS_SELECTOR, ".tleftbox a")
    print(f"[DEBUG] 找到 a 标签数量：{len(link_elements)}")

    hrefs = set()
    for el in link_elements:
        href = el.get_attribute("href")
        if href and re.match(r"^https://www\.tgb\.cn/blog/2166241/\d+$", href):
            hrefs.add(href)

    with open(output_file, "w", encoding="utf-8") as f:
        for link in sorted(hrefs):
            f.write(link + "\n")

    print(f"✅ 共提取 {len(hrefs)} 条链接，已保存到 {output_file}")

def run():
    driver = create_driver()
    try:
        blogcat_url = "https://www.tgb.cn/user/blog/blogcata?userID=2166241&bcID=41071"
        output_file = "blog_links-auto.txt"
        extract_links(driver, blogcat_url, output_file)
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
