from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com/travel/flights")
    page.wait_for_timeout(8000)
    print(page.title())
    browser.close()