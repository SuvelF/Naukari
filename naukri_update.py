from playwright.sync_api import sync_playwright
import os
import time
import random
import re

NAUKRI_EMAIL = os.environ.get("NAUKRI_EMAIL")
NAUKRI_PASSWORD = os.environ.get("NAUKRI_PASSWORD")

SKILLS_POOL = [
    "Core Java", "DevOps", "Spring Boot", "REST API", "Microservices", 
    "JPA", "Hibernate", "SQL", "Spring MVC", "JDBC", "SOAP", "Agile", 
    "Maven", "Jira", "Git", "AWS", "EC2", "Unit Testing", "Web Services", 
    "CI/CD", "Kafka", "JSON", "Spring Cloud", "Docker", "Jenkins", 
    "Kubernetes", "Spring Security", "Spring Batch", "Redis", "PostgreSQL", "MongoDB"
]

def get_new_headline(current_headline):
    print(f"Current Headline: {current_headline}")
    
    present_skills = []
    not_present_skills = []
    
    for skill in SKILLS_POOL:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, current_headline, flags=re.IGNORECASE):
            present_skills.append(skill)
        else:
            not_present_skills.append(skill)
    
    print(f"Present: {present_skills}")
    print(f"Not Present: {not_present_skills}")
    
    new_headline = current_headline
    
    # 1. REMOVE 1 skill
    if present_skills:
        skill_to_remove = random.choice(present_skills)
        print(f"Removing: {skill_to_remove}")
        pattern_remove = r"\b" + re.escape(skill_to_remove) + r"\b"
        new_headline = re.sub(pattern_remove, "", new_headline, flags=re.IGNORECASE)
        new_headline = re.sub(r"\s*,\s*,\s*", ", ", new_headline)
        new_headline = re.sub(r"\s*\|\s*\|\s*", " | ", new_headline)
        new_headline = re.sub(r"\s*,\s*\|\s*", " | ", new_headline)
        new_headline = re.sub(r"\s*\|\s*,\s*", " | ", new_headline)
        new_headline = re.sub(r"\s{2,}", " ", new_headline)
        new_headline = new_headline.strip(" ,|")
        new_headline = re.sub(r",\s*,", ",", new_headline)

    # 2. ADD 1 new skill
    if not_present_skills:
        skill_to_add = random.choice(not_present_skills)
        print(f"Adding: {skill_to_add}")
        if new_headline.endswith("|"):
            new_headline = f"{new_headline} {skill_to_add}"
        else:
            new_headline = f"{new_headline}, {skill_to_add}"
    
    if len(new_headline) > 250:
        new_headline = new_headline[:250].rsplit(",", 1)[0]

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

            print("Opening Resume Headline edit...")
            page.locator("xpath=//span[contains(text(),\'Resume headline\')]/../..//span[contains(text(),\'edit\')]").first.click()
            page.wait_for_timeout(3000)

            textarea = page.locator("textarea").first
            if textarea.count() == 0:
                textarea = page.locator("#resumeHeadlineTxt")
            
            textarea.wait_for(timeout=10000)
            current_headline = textarea.input_value()
            
            new_headline = get_new_headline(current_headline)
            
            textarea.fill(new_headline)
            page.wait_for_timeout(1000)
            
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
