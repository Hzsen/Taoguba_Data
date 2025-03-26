from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

BASE_URL = "https://www.tgb.cn"
TARGET_URL = "https://www.tgb.cn/user/blog/blogcata?userID=2166241&bcID=41071"
OUTPUT_FILE = "blog_links-auto.txt"

def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--user-data-dir=/Users/hzs/selenium-chrome-profile")
    options.add_argument("--profile-directory=Default")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def extract_links(driver):
    print(f"🔍 正在访问：{TARGET_URL}")
    driver.get(TARGET_URL)

    # 给 JS 动态渲染留时间
    time.sleep(3)

    # ✅ 不要切换 iframe！直接查找文章链接
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.yinchan"))
        )
        link_elements = driver.find_elements(By.CSS_SELECTOR, "a.yinchan")
    except Exception as e:
        print(f"[❌ 链接未加载] {e}")
        return []

    print(f"✅ 抓到 {len(link_elements)} 个文章链接")

    hrefs = set()
    for el in link_elements:
        href = el.get_attribute("href")
        if href and not href.startswith("http"):
            href = BASE_URL + "/" + href.lstrip("/")
        hrefs.add(href)

    return sorted(hrefs)



def save_links(hrefs):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for link in hrefs:
            f.write(link + "\n")
    print(f"✅ 已保存到 {OUTPUT_FILE}")

def run():
    driver = create_driver()
    try:
        links = extract_links(driver)
        save_links(links)
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
