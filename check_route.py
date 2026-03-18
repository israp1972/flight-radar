from playwright.sync_api import sync_playwright

URL = "https://www.google.com/travel/flights"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    print("Haz tu búsqueda manual en la ventana del navegador.")
    print("Cuando termines, copia la URL desde la barra del navegador.")
    input("Después de copiar la URL, presiona ENTER aquí para cerrar...")
    browser.close()