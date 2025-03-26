from playwright.sync_api import sync_playwright
import time
import os
import json
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
USERNAME = os.getenv('TGB_USERNAME')
PASSWORD = os.getenv('TGB_PASSWORD')

def save_cookies(context, filename="tgb_cookies.json"):
    """Save browser cookies to a file"""
    cookies = context.cookies()
    with open(filename, "w") as f:
        json.dump(cookies, f)
    print(f"Cookies saved to {filename}")

def load_cookies(context, filename="tgb_cookies.json"):
    """Load cookies from file into browser context"""
    try:
        with open(filename, "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print(f"Cookies loaded from {filename}")
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"No valid cookie file found at {filename}")
        return False

def check_login_status(page):
    """Check if user is logged in"""
    try:
        # Wait a bit for the page to update after login
        time.sleep(2)
        
        # Check for elements that indicate logged-in state
        is_logged_in = (
            page.is_visible("a:has-text('退出')") or 
            page.is_visible(".user-avatar") or
            page.is_visible(".user-name") or
            not page.is_visible("a[onclick='javascript:loginPanel();']")
        )
        
        if is_logged_in:
            print("User is logged in")
        else:
            print("User is not logged in")
        
        return is_logged_in
    except Exception as e:
        print(f"Error checking login status: {e}")
        return False

def automatic_login(page):
    """Perform automatic login"""
    try:
        # Open login panel
        print("Opening login panel...")
        page.click("a[onclick='javascript:loginPanel();']")
        
        # Wait for the login panel to appear and fully load
        print("Waiting for login panel to fully load...")
        page.wait_for_selector("#userLoginBtn", state="visible", timeout=10000)
        time.sleep(2)
        
        # Click on the account login tab
        print("Switching to account login...")
        page.click("#userLoginBtn")
        
        # Wait for the form to load
        page.wait_for_selector("#userPanelName", state="visible", timeout=10000)
        page.wait_for_selector("#userPanelPwd", state="visible", timeout=10000)
        time.sleep(2)
        
        # Fill in credentials
        print("Entering username...")
        page.fill("#userPanelName", USERNAME)
        time.sleep(random.uniform(0.8, 1.5))  # Random delay to appear more human-like
        
        print("Entering password...")
        page.fill("#userPanelPwd", PASSWORD)
        time.sleep(random.uniform(1.0, 2.0))  # Wait after filling credentials
        
        # Make sure the button is visible in viewport
        page.evaluate("document.querySelector('#loginBtn').scrollIntoView({behavior: 'smooth', block: 'center'})")
        time.sleep(1)
        
        # Click the login button
        print("Clicking login button...")
        page.click("#loginBtn", force=True)
        
        # Wait for login process to complete
        print("Waiting for login to complete...")
        time.sleep(5)
        
        # Check if login was successful
        return check_login_status(page)
        
    except Exception as e:
        print(f"Error during automatic login: {e}")
        return False

def main():
    with sync_playwright() as p:
        # Launch Firefox browser
        print("Launching Firefox browser...")
        
        # Set user agent to appear as a regular browser
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
        
        # Launch browser with specific options
        browser = p.firefox.launch(
            headless=False, 
            slow_mo=50,
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
        
        page = context.new_page()
        
        # Try to use saved cookies first
        has_cookies = load_cookies(context)
        
        # Navigate to the forum
        print("Navigating to the forum...")
        page.goto("https://www.tgb.cn/blog/2166241")
        page.wait_for_load_state("networkidle")
        
        # Check if we're already logged in with the cookies
        if has_cookies and check_login_status(page):
            print("Successfully logged in using saved cookies")
        else:
            print("Need to log in automatically")
            # Perform automatic login
            if automatic_login(page):
                print("Login successful, saving cookies for future use")
                save_cookies(context)
            else:
                print("Login failed or could not be verified")
        
        # Take a final screenshot
        page.screenshot(path="final_state.png")
        print("Screenshot saved as final_state.png")
        
        # Close the browser
        print("Login process completed. Closing browser.")
        browser.close()

if __name__ == "__main__":
    main() 