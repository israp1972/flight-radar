from playwright.sync_api import sync_playwright

URL = "https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI2LTA1LTEyagwIAhIIL20vMGxwZmhyBwgBEgNFWkUaIxIKMjAyNi0wNS0xOGoHCAESA0VaRXIMCAISCC9tLzBscGZoQAFIAXABggELCP___________wGYAQE&hl=en&curr=USD"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)

    text = page.locator("body").inner_text()
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    start_index = None
    for i, line in enumerate(lines):
        if "Top departing flights" in line:
            start_index = i
            break

    if start_index is None:
        print("No se encontró la sección 'Top departing flights'.")
    else:
        print("=== BLOQUE CERCA DE TOP DEPARTING FLIGHTS ===")
        for line in lines[start_index:start_index + 60]:
            print(line)

    input("Presiona ENTER para cerrar...")
    browser.close()