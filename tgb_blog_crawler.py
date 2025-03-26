from playwright.sync_api import sync_playwright
import time
import os
import json
import re
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Blog section URLs
BLOG_SECTIONS = [
    "https://www.tgb.cn/user/blog/blogcata?userID=2166241&bcID=0",
    "https://www.tgb.cn/user/blog/blogcata?userID=2166241&bcID=41077",
    "https://www.tgb.cn/user/blog/blogcata?userID=2166241&bcID=41070",
    "https://www.tgb.cn/user/blog/blogcata?userID=2166241&bcID=40976",
    "https://www.tgb.cn/user/blog/blogcata?userID=2166241&bcID=41071"
]

def load_cookies(context, filename="tgb_cookies.json"):
    """Load cookies from file into browser context"""
    try:
        with open(filename, "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print(f"Cookies loaded from {filename}")
        return True
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"No valid cookie file found at {filename}: {e}")
        return False

def extract_section_id(url):
    """Extract the section ID from the URL"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('bcID', ['unknown'])[0]

def extract_blog_links(page):
    """Extract blog links from the current page"""
    links = []
    
    # Find all blog post links
    link_elements = page.query_selector_all('td.table_bottom01 a.yinchan')
    
    for link in link_elements:
        href = link.get_attribute('href')
        title = link.get_attribute('title')
        
        # Get the views/replies from the next cell
        views_replies = link.evaluate('el => el.closest("tr").querySelector("td:nth-child(4)").textContent.trim()')
        
        # Get the date from the last cell
        date = link.evaluate('el => el.closest("tr").querySelector("td:nth-child(5)").textContent.trim()')
        
        if href:
            # Construct the full URL if it's a relative path
            if href.startswith('a/'):
                full_url = f"https://www.tgb.cn/{href}"
            else:
                full_url = href
                
            links.append({
                'url': full_url,
                'title': title,
                'views_replies': views_replies,
                'date': date
            })
    
    return links

def check_for_pagination(page):
    """Check if there are more pages and navigate to them"""
    # Look for pagination links
    next_page_link = page.query_selector('td.font4 a:has-text("下一页")')
    
    if next_page_link and not next_page_link.evaluate('el => el.closest("tr").textContent.includes("下一页 末页")'):
        # Click the next page link
        next_page_link.click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Wait for the page to stabilize
        return True
    
    return False

def crawl_section(page, section_url):
    """Crawl a single section and extract all blog links"""
    section_id = extract_section_id(section_url)
    print(f"\nCrawling section {section_id}...")
    
    # Navigate to the section
    page.goto(section_url)
    page.wait_for_load_state("networkidle")
    time.sleep(2)  # Wait for the page to stabilize
    
    all_links = []
    page_num = 1
    
    # Process the first page
    print(f"Processing page {page_num}...")
    links = extract_blog_links(page)
    all_links.extend(links)
    print(f"Found {len(links)} links on page {page_num}")
    
    # Check for and process additional pages
    while check_for_pagination(page):
        page_num += 1
        print(f"Processing page {page_num}...")
        links = extract_blog_links(page)
        all_links.extend(links)
        print(f"Found {len(links)} links on page {page_num}")
    
    print(f"Total links found in section {section_id}: {len(all_links)}")
    return section_id, all_links

def save_links_to_file(section_id, links, output_dir="blog_links"):
    """Save the extracted links to a file"""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a file for this section
    filename = os.path.join(output_dir, f"section_{section_id}.txt")
    
    with open(filename, "w", encoding="utf-8") as f:
        for link in links:
            f.write(f"{link['url']}\t{link['title']}\t{link['views_replies']}\t{link['date']}\n")
    
    print(f"Saved {len(links)} links to {filename}")

def save_all_links(all_sections_links, output_dir="blog_links"):
    """Save all links to a combined file"""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a combined file with all links
    filename = os.path.join(output_dir, "all_links.txt")
    
    with open(filename, "w", encoding="utf-8") as f:
        for section_id, links in all_sections_links.items():
            f.write(f"# Section {section_id} - {len(links)} links\n")
            for link in links:
                f.write(f"{link['url']}\t{link['title']}\t{link['views_replies']}\t{link['date']}\n")
            f.write("\n")
    
    # Create a file with just the URLs for easy processing
    url_filename = os.path.join(output_dir, "all_urls.txt")
    with open(url_filename, "w", encoding="utf-8") as f:
        for section_id, links in all_sections_links.items():
            for link in links:
                f.write(f"{link['url']}\n")
    
    print(f"Saved all links to {filename}")
    print(f"Saved all URLs to {url_filename}")

def main():
    with sync_playwright() as p:
        # Launch Firefox browser
        print("Launching Firefox browser...")
        
        # Set user agent to appear as a regular browser
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        
        # Launch browser with specific options
        browser = p.firefox.launch(
            headless=True,  # Run headless for crawling
            slow_mo=20,
        )
        
        context = browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",  # Set locale to Chinese
        )
        
        # Add some human-like behavior
        context.add_init_script("""
            // Override the navigator properties
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
        """)
        
        # Load cookies
        if not load_cookies(context):
            print("Failed to load cookies. Please run the login script first.")
            browser.close()
            return
        
        page = context.new_page()
        
        # Crawl each section
        all_sections_links = {}
        
        for section_url in BLOG_SECTIONS:
            section_id, links = crawl_section(page, section_url)
            all_sections_links[section_id] = links
            
            # Save links for this section
            save_links_to_file(section_id, links)
            
            # Add a small delay between sections
            time.sleep(2)
        
        # Save all links to a combined file
        save_all_links(all_sections_links)
        
        # Close the browser
        print("\nCrawling completed. Closing browser.")
        browser.close()

if __name__ == "__main__":
    main() 