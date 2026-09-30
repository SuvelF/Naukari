from playwright.sync_api import sync_playwright
import os
import time
import random
import re

NAUKRI_EMAIL = os.environ.get("NAUKRI_EMAIL")
NAUKRI_PASSWORD = os.environ.get("NAUKRI_PASSWORD")

# Skills pool to rotate - You can edit this list
JAVA_SKILLS = ["Core Java", "Spring Boot", "Hibernate", "Microservices", "REST API", "AWS", "Docker", "Kubernetes", "MySQL", "J2EE", "Spring MVC", "Java 8"]

def get_new_headline(current_headline):
    print(f"Current Headline: {current_headline}")
    
    # Find which skills from pool are already present in headline
    present_skills = [skill for skill in JAVA_SKILLS if skill.lower() in current_headline.lower()]
    not_present_skills = [skill for skill in JAVA_SKILLS if skill.lower() not in current_headline.lower()]
    
    new_headline = current_headline
    
    # 1. Remove 1 skill if present
    if present_skills:
        skill_to_remove = random.choice(present_skills)
        print(f"Removing: {skill_to_remove}")
        # Remove skill case-insensitive
        new_headline = re.sub(re.escape(skill_to_remove), "", new_headline, flags=re.IGNORECASE)
        # Clean extra separators like ,, || or double spaces
        new_headline = re.sub(r\'\s*[\|,]\s*[\|,]\s*\', \' | \', new_headline)
        new_headline = re.sub(r\'\s{2,}\', \' \', new_headline).strip(" |,")
    
    # 2. Add 1 new skill if available
    if not_present_skills:
        skill_to_add = random.choice(not_present_skills)
        print(f"Adding: {skill_to_add}")
        # Add with separator
        if len(new_headline) > 0:
            new_headline = f"{new_headline} | {skill_to_add}"
        else:
            new_headline = skill_to_add
    
    # Naukri limit is 250 characters
    new_headline = new_headline[:250]
    
    print(f"New Headline: {new_headline}")
    return new_headline

def update_naukri():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Logging in...")
            page.goto("https://www.naukri.com/nlogin/login", timeout=60000)
            page.wait_for_timeout(3000)
            page.fill("#usernameField", NAUKRI_EMAIL)
            page.fill("#passwordField", NAUKRI_PASSWORD)
            page.click("button[type=\'submit\']")
            page.wait_for_timeout(8000)

            print("Going to profile...")
            page.goto("https://www.naukri.com/mnjuser/profile", timeout=60000)
            page.wait_for_timeout(7000)

            # Click edit on Resume Headline
            print("Opening Resume Headline edit...")
            page.locator("xpath=//span[contains(text(),\'Resume headline\')]/../..//span[contains(text(),\'edit\')]").first.click()
            page.wait_for_timeout(3000)

            # Get current headline text from textarea
            textarea = page.locator("textarea").first
            # Naukri sometimes uses input with id resumeHeadlineTxt
            if textarea.count() == 0:
                textarea = page.locator("#resumeHeadlineTxt")
            
            textarea.wait_for(timeout=10000)
            current_headline = textarea.input_value()
            
            new_headline = get_new_headline(current_headline)
            
            # Fill new headline
            textarea.fill(new_headline)
            page.wait_for_timeout(1000)
            
            # Save
            page.locator("xpath=//button[text()=\'Save\']").click()
            page.wait_for_timeout(4000)
            
            print(f"SUCCESS: Profile Updated at {time.ctime()}")
            page.screenshot(path="proof.png")
            
        except Exception as e:
            print(f"FAILED: {e}")
            page.screenshot(path="error.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    update_naukri()
