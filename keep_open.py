from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com/travel/flights?hl=en", wait_until="domcontentloaded")
    print("Página abierta. Revísala manualmente.")
    input("Presiona ENTER en PowerShell para cerrar...")
    browser.close()