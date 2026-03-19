from playwright.sync_api import sync_playwright

URL = "https://www.skyscanner.com/transport/flights/lima/bue/260512/260518/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Abriendo Skyscanner...")
    page.goto(URL, wait_until="domcontentloaded")

    page.wait_for_timeout(15000)

    text = page.locator("body").inner_text()

    print("=== TEXTO CAPTURADO ===")
    print(text[:2000])  # solo primeros caracteres

    browser.close()