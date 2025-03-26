from playwright.sync_api import sync_playwright
import time
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
from pathlib import Path
import shutil
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    # Replace invalid characters with underscore
    invalid_chars = r'[\\/*?:"<>|]'
    sanitized = re.sub(invalid_chars, "_", filename)
    # Limit length to avoid path too long errors
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."
    return sanitized

def extract_post_content(page):
    """Extract the main content of the blog post"""
    try:
        # Wait for the content to load with increased timeout
        page.wait_for_selector(".article-text", state="visible", timeout=30000)
        
        # Wait a bit more to ensure everything is loaded
        time.sleep(3)
        
        # Get the HTML content
        content_html = page.query_selector(".article-text").inner_html()
        
        # Get the title
        title = page.title()
        
        return title, content_html
    except Exception as e:
        print(f"Error extracting content: {e}")
        # Take a screenshot for debugging
        page.screenshot(path="error_extract.png")
        raise

def process_html_content(html_content):
    """Process the HTML content to extract text and image links"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process images
    images = []
    for img in soup.find_all('img', {'data-type': 'contentImage'}):
        if img.get('src'):
            images.append(img['src'])
    
    # Clean up the HTML to keep only text and image placeholders
    processed_html = html_content
    
    # Replace image tags with placeholders
    for i, img_tag in enumerate(soup.find_all('img', {'data-type': 'contentImage'})):
        if img_tag.get('src'):
            img_placeholder = f"img: {img_tag['src']}\n"
            processed_html = processed_html.replace(str(img_tag), img_placeholder)
    
    return processed_html, images

def format_text_with_images(html_content):
    """Format text content with image links in the requested format"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Replace image tags with the requested format
    for img_tag in soup.find_all('img', {'data-type': 'contentImage'}):
        if img_tag.get('src'):
            img_placeholder = f"\n<img: {img_tag['src']}>\n"
            img_tag.replace_with(BeautifulSoup(img_placeholder, 'html.parser'))
    
    # Get the text content
    text_content = soup.get_text(separator="\n")
    
    # Clean up extra newlines
    text_content = re.sub(r'\n{3,}', '\n\n', text_content)
    
    return text_content

def download_image(url, folder_path):
    """Download an image and save it to the specified folder"""
    try:
        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(unquote(parsed_url.path))
        
        # Remove query parameters if any
        filename = filename.split('?')[0]
        
        # Create full path
        file_path = os.path.join(folder_path, filename)
        
        # Download the image
        response = requests.get(url, stream=True, timeout=20)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        print(f"Downloaded image: {filename}")
        return filename
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def download_post(page, url, output_dir="blog_posts"):
    """Download a single blog post and its images"""
    try:
        print(f"\nDownloading post: {url}")
        
        # Navigate to the post with longer timeout
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        time.sleep(3)  # Wait longer for the page to stabilize
        
        # Extract post content
        title, content_html = extract_post_content(page)
        
        # Create sanitized title for folder name
        folder_name = sanitize_filename(title)
        folder_path = os.path.join(output_dir, folder_name)
        
        # Create folder for this post
        os.makedirs(folder_path, exist_ok=True)
        
        # Process HTML content
        processed_html, images = process_html_content(content_html)
        
        # Save the processed HTML
        html_file_path = os.path.join(folder_path, "content.html")
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(processed_html)
        
        # Save the text content with image links in the requested format
        text_file_path = os.path.join(folder_path, "content.txt")
        with open(text_file_path, "w", encoding="utf-8") as f:
            text_content = format_text_with_images(content_html)
            f.write(text_content)
        
        # Create images folder
        images_folder = os.path.join(folder_path, "images")
        os.makedirs(images_folder, exist_ok=True)
        
        # Download images
        for img_url in images:
            download_image(img_url, images_folder)
        
        # Save metadata
        metadata = {
            "title": title,
            "url": url,
            "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "image_count": len(images)
        }
        
        metadata_path = os.path.join(folder_path, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully downloaded post: {title}")
        print(f"Saved to: {folder_path}")
        print(f"Images: {len(images)}")
        
        return True
    except Exception as e:
        print(f"Error downloading post {url}: {e}")
        # Take a screenshot for debugging
        try:
            error_dir = os.path.join(output_dir, "errors")
            os.makedirs(error_dir, exist_ok=True)
            page.screenshot(path=os.path.join(error_dir, f"error_{int(time.time())}.png"))
        except:
            pass
        return False, url

def load_urls(filename="blog_links/all_urls.txt"):
    """Load URLs from the file"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(urls)} URLs from {filename}")
        return urls
    except Exception as e:
        print(f"Error loading URLs from {filename}: {e}")
        return []

def save_error_urls(error_urls, filename="error_urls.txt"):
    """Save URLs that failed to download"""
    with open(filename, "w", encoding="utf-8") as f:
        for url in error_urls:
            f.write(f"{url}\n")
    print(f"Saved {len(error_urls)} error URLs to {filename}")

def main():
    # Create output directory
    output_dir = "blog_posts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Load URLs
    urls = load_urls()
    if not urls:
        print("No URLs to process. Exiting.")
        return
    
    # Track error URLs
    error_urls = []
    
    with sync_playwright() as p:
        # Launch Firefox browser
        print("Launching Firefox browser...")
        
        # Set user agent to appear as a regular browser
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        
        # Launch browser with specific options
        browser = p.firefox.launch(
            headless=True,  # Run headless for downloading
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
        
        # Set the default timeout on the page instead
        page.set_default_timeout(60000)
        
        # Download each post
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls):
            print(f"\nProcessing {i+1}/{len(urls)}: {url}")
            
            result = download_post(page, url, output_dir)
            if isinstance(result, tuple):
                failed += 1
                error_urls.append(result[1])
            else:
                if result:
                    successful += 1
                else:
                    failed += 1
                    error_urls.append(url)
            
            # Add a small delay between downloads to avoid overloading the server
            time.sleep(2)
            
            # Save error URLs periodically
            if i % 10 == 0 and error_urls:
                save_error_urls(error_urls)
        
        # Save final error URLs
        if error_urls:
            save_error_urls(error_urls)
        
        # Print summary
        print("\n" + "="*50)
        print(f"Download Summary:")
        print(f"Total URLs: {len(urls)}")
        print(f"Successfully downloaded: {successful}")
        print(f"Failed: {failed}")
        print(f"Error URLs saved to: error_urls.txt")
        print("="*50)
        
        # Close the browser
        print("\nDownloading completed. Closing browser.")
        browser.close()

if __name__ == "__main__":
    main() 