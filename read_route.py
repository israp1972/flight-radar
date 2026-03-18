from playwright.sync_api import sync_playwright
import re

URL = "https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI2LTA0LTEyagwIAhIIL20vMGxwZmhyBwgBEgNNQUQaIxIKMjAyNi0wNC0xOWoHCAESA01BRHIMCAISCC9tLzBscGZoQAFAAUgBcAGCAQsI____________AZgBAQ"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)

    text = page.locator("body").inner_text()

    raw_prices = re.findall(r"PEN\s?\d[\d.,]*", text)

    numeric_prices = []
    for price in raw_prices:
        cleaned = (
            price.replace("PEN", "")
            .replace("\u00a0", "")
            .replace(" ", "")
            .replace(",", "")
            .strip()
        )
        if cleaned.isdigit():
            numeric_prices.append(int(cleaned))

    unique_prices = sorted(set(numeric_prices))

    print("=== PRECIOS ÚNICOS ===")
    for price in unique_prices:
        print(f"PEN {price:,}")

    print()
    print(f"TOTAL ÚNICOS: {len(unique_prices)}")

    if unique_prices:
        print(f"MÍNIMO: PEN {min(unique_prices):,}")
        print(f"MÁXIMO: PEN {max(unique_prices):,}")

    input("Presiona ENTER para cerrar...")
    browser.close()