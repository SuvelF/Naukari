from playwright.sync_api import sync_playwright
import time

NAUKRI_EMAIL = "YOUR_EMAIL"  # will be replaced by GitHub Secret
NAUKRI_PASSWORD = "YOUR_PASSWORD"

def update_naukri():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Logging in...")
            page.goto("https://www.naukri.com/nlogin/login", timeout=60000)
            page.fill("#usernameField", NAUKRI_EMAIL)
            page.fill("#passwordField", NAUKRI_PASSWORD)
            page.click("button[type=\'submit\']")
            page.wait_for_timeout(7000)

            print("Going to profile...")
            page.goto("https://www.naukri.com/mnjuser/profile", timeout=60000)
            page.wait_for_timeout(7000)

            # Refresh trick - Edit Resume Headline and Save again
            # This updates your \'Last Updated\' to today
            page.click("xpath=//span[contains(text(),\'Resume headline\')]/../..//span[contains(text(),\'edit\')]")
            page.wait_for_timeout(3000)
            # Just click save without changing anything
            page.click("xpath=//button[text()=\'Save\']")
            page.wait_for_timeout(3000)
            
            print(f"SUCCESS: Profile Updated at {time.ctime()}")
            page.screenshot(path="proof.png")
        except Exception as e:
            print(f"FAILED: {e}")
            page.screenshot(path="error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    update_naukri()
