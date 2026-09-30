from playwright.sync_api import sync_playwright
import os
import time
import random
import re

NAUKRI_EMAIL = os.environ.get("NAUKRI_EMAIL", "").strip()
NAUKRI_PASSWORD = os.environ.get("NAUKRI_PASSWORD", "").strip()

SKILLS_POOL = [
    "Core Java", "DevOps", "Spring Boot", "REST API", "Microservices", 
    "JPA", "Hibernate", "SQL", "Spring MVC", "JDBC", "SOAP", "Agile", 
    "Maven", "Jira", "Git", "AWS", "EC2", "Unit Testing", "Web Services", 
    "CI/CD", "Kafka", "JSON", "Spring Cloud", "Docker", "Jenkins", 
    "Kubernetes", "Spring Security", "Spring Batch", "Redis", "PostgreSQL", "MongoDB"
]

def get_new_headline(current_headline):
    print(f"Current Headline: {current_headline}", flush=True)
    present_skills = []
    not_present_skills = []
    for skill in SKILLS_POOL:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, current_headline, flags=re.IGNORECASE):
            present_skills.append(skill)
        else:
            not_present_skills.append(skill)
    
    new_headline = current_headline
    if present_skills:
        skill_to_remove = random.choice(present_skills)
        print(f"Removing: {skill_to_remove}", flush=True)
        pattern_remove = r"\b" + re.escape(skill_to_remove) + r"\b"
        new_headline = re.sub(pattern_remove, "", new_headline, flags=re.IGNORECASE)
        new_headline = re.sub(r"\s*,\s*,\s*", ", ", new_headline)
        new_headline = re.sub(r"\s*\|\s*\|\s*", " | ", new_headline)
        new_headline = re.sub(r"\s{2,}", " ", new_headline)
        new_headline = new_headline.strip(" ,|")

    if not_present_skills:
        skill_to_add = random.choice(not_present_skills)
        print(f"Adding: {skill_to_add}", flush=True)
        if new_headline.endswith("|"):
            new_headline = f"{new_headline} {skill_to_add}"
        else:
            new_headline = f"{new_headline}, {skill_to_add}"
    
    if len(new_headline) > 250:
        new_headline = new_headline[:250].rsplit(",", 1)[0]
    print(f"New Headline: {new_headline}", flush=True)
    return new_headline

def update_naukri():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()
        try:
            print(f"Email present: {bool(NAUKRI_EMAIL)} Length: {len(NAUKRI_EMAIL) if NAUKRI_EMAIL else 0}", flush=True)
            print("Step 1: Opening login page...", flush=True)
            page.goto("https://www.naukri.com/nlogin/login", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(7000)
            page.screenshot(path="1_login_page.png")
            
            # NEW - Flexible locator for Naukri\'s new design
            print("Looking for login fields...", flush=True)
            username_locator = page.locator(\'input[placeholder*="Email"], input[placeholder*="Username"], #usernameField\').first
            password_locator = page.locator(\'input[type="password"], #passwordField\').first
            login_btn = page.locator(\'button:has-text("Login")\').first

            username_locator.wait_for(state="visible", timeout=20000)
            print("Filling credentials...", flush=True)
            username_locator.fill(NAUKRI_EMAIL)
            password_locator.fill(NAUKRI_PASSWORD)
            login_btn.click()
            
            page.wait_for_timeout(8000)
            page.screenshot(path="2_after_login.png")
            print(f"After login URL: {page.url}", flush=True)
            
            if "nlogin" in page.url:
                print("STILL on login page - Email/Password wrong or blocked", flush=True)
                print(page.content()[:2000])
                raise Exception("Login failed - Check Secrets NAUKRI_EMAIL / NAUKRI_PASSWORD")

            print("Step 2: Going to profile...", flush=True)
            page.goto("https://www.naukri.com/mnjuser/profile", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(7000)
            page.screenshot(path="3_profile.png")

            print("Step 3: Editing Resume Headline...", flush=True)
            edit_btn = page.locator("span:has-text(\'editOneTheme\'), span:has-text(\'edit\')").first
            # fallback for new UI
            if edit_btn.count() == 0:
                edit_btn = page.locator("xpath=//span[contains(text(),\'Resume headline\')]/../..//span[contains(text(),\'edit\')]").first
            edit_btn.click()
            page.wait_for_timeout(3000)

            textarea = page.locator("textarea#resumeHeadlineTxt").first
            if textarea.count() == 0:
                textarea = page.locator("textarea").first
            textarea.wait_for(timeout=10000)
            current_headline = textarea.input_value()
            
            new_headline = get_new_headline(current_headline)
            textarea.fill(new_headline)
            page.wait_for_timeout(1000)
            
            page.locator("button:has-text(\'Save\')").first.click()
            page.wait_for_timeout(4000)
            page.screenshot(path="proof.png")
            print(f"SUCCESS: Profile Updated at {time.ctime()}", flush=True)
            
        except Exception as e:
            print(f"FAILED: {e}", flush=True)
            page.screenshot(path="error.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    update_naukri()
