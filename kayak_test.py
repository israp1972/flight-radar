from playwright.sync_api import sync_playwright

# Ruta Lima → Buenos Aires
URL = "https://www.kayak.com/flights/LIM-BUE/2026-05-12/2026-05-18"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Abriendo Kayak...")
    page.goto(URL, wait_until="domcontentloaded")

    # Espera para que cargue contenido dinámico
    page.wait_for_timeout(15000)

    text = page.locator("body").inner_text()

    print("=== TEXTO CAPTURADO ===")
    print(text[:2000])

    browser.close()