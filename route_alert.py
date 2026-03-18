from playwright.sync_api import sync_playwright
import re
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1483789945079333014/ZF_mb7h-A3q9Vr681SpL0YVal-vHIeOxXuXcAoQI1Jgub7y5v5s8IWoAwJHuBp8qhfyY"

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

    if unique_prices:
        min_price = min(unique_prices)
        max_price = max(unique_prices)

        message = (
            "✈️ Radar de vuelos\n"
            "Ruta: Lima → Madrid\n"
            f"Precio mínimo detectado: PEN {min_price:,}\n"
            f"Precio máximo detectado: PEN {max_price:,}\n"
            f"Total de precios únicos: {len(unique_prices)}"
        )

        print(message)
        requests.post(WEBHOOK_URL, json={"content": message})
    else:
        print("No se detectaron precios.")

    input("Presiona ENTER para cerrar...")
    browser.close()