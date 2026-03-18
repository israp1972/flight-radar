from playwright.sync_api import sync_playwright
import re

URL = "https://www.google.com/travel/flights?hl=en"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    text = page.locator("body").inner_text()

    # buscar precios tipo PEN 384
    prices = re.findall(r"PEN\s?\d+", text)

    print("=== PRECIOS DETECTADOS ===")
    for price in prices:
        print(price)

    print("=== TOTAL ===", len(prices))

    input("Presiona ENTER para cerrar...")
    browser.close()