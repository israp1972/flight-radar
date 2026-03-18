from playwright.sync_api import sync_playwright
import re

URL = "https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI2LTA1LTEyagwIAhIIL20vMGxwZmhyBwgBEgNFWkUaIxIKMjAyNi0wNS0xOGoHCAESA0VaRXIMCAISCC9tLzBscGZoQAFIAXABggELCP___________wGYAQE&hl=en&curr=USD"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)

    text = page.locator("body").inner_text()

    raw_prices = re.findall(r"\$\d[\d,]*", text)

    numeric_prices = []
    for price in raw_prices:
        cleaned = (
            price.replace("$", "")
            .replace(",", "")
            .strip()
        )
        if cleaned.isdigit():
            numeric_prices.append(int(cleaned))

    unique_prices = sorted(set(numeric_prices))

    print("=== PRECIOS ÚNICOS USD ===")
    for price in unique_prices:
        print(f"USD {price:,}")

    print()
    print(f"TOTAL ÚNICOS: {len(unique_prices)}")

    if unique_prices:
        print(f"MÍNIMO: USD {min(unique_prices):,}")
        print(f"MÁXIMO: USD {max(unique_prices):,}")

    input("Presiona ENTER para cerrar...")
    browser.close()