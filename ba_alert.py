import os
import re
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
print(f"WEBHOOK_URL cargado: {bool(WEBHOOK_URL)}")

test_response = requests.post(
    WEBHOOK_URL,
    json={"content": "🚨 TEST DESDE GITHUB ACTIONS 🚨"}
)
print(f"Discord status: {test_response.status_code}")
print(test_response.text[:200])

raise SystemExit("Prueba terminada")
URL = "https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI2LTA1LTEyagwIAhIIL20vMGxwZmhyBwgBEgNFWkUaIxIKMjAyNi0wNS0xOGoHCAESA0VaRXIMCAISCC9tLzBscGZoQAFIAXABggELCP___________wGYAQE&hl=en&curr=USD"

MAX_PRICE = 700
MAX_DURATION_ONE_STOP_HOURS = 8

def parse_duration_hours(text: str):
    m = re.search(r"(\d+)\s*hr(?:\s*(\d+)\s*min)?", text.lower())
    if not m:
        return None
    hours = int(m.group(1))
    minutes = int(m.group(2)) if m.group(2) else 0
    return hours + minutes / 60.0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
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
        print("No se encontró la sección de vuelos.")
        input("Presiona ENTER para cerrar...")
        browser.close()
        raise SystemExit

    section = lines[start_index:start_index + 120]

    flights = []
    current = []

    for line in section:
        if re.fullmatch(r"\$\d[\d,]*", line):
            current.append(line)
            flights.append(current)
            current = []
        else:
            current.append(line)

    parsed = []

    for block in flights:
        price = None
        duration_h = None
        stop_type = None
        route = None

        for line in block:
            if price is None and re.fullmatch(r"\$\d[\d,]*", line):
                price = int(line.replace("$", "").replace(",", ""))

            if duration_h is None and "hr" in line.lower():
                parsed_duration = parse_duration_hours(line)
                if parsed_duration is not None:
                    duration_h = parsed_duration

            if stop_type is None:
                low = line.lower()
                if "nonstop" in low:
                    stop_type = "direct"
                elif "1 stop" in low:
                    stop_type = "1_stop"

            if route is None and "LIM–EZE" in line:
                route = line

        if price is not None:
            parsed.append({
                "price": price,
                "duration_h": duration_h,
                "stop_type": stop_type,
                "route": route,
                "block": block
            })

    direct_matches = [
        f for f in parsed
        if f["stop_type"] == "direct" and f["price"] <= MAX_PRICE
    ]

    one_stop_matches = [
        f for f in parsed
        if f["stop_type"] == "1_stop"
        and f["price"] <= MAX_PRICE
        and f["duration_h"] is not None
        and f["duration_h"] <= MAX_DURATION_ONE_STOP_HOURS
    ]

    print("=== RESUMEN ===")
    print(f"Directos válidos: {len(direct_matches)}")
    print(f"1 escala válidos: {len(one_stop_matches)}")

        print(f"WEBHOOK_URL cargado: {bool(WEBHOOK_URL)}")
print("FORZANDO ENVÍO DE PRUEBA")

test_message = "🚨 TEST DISCORD OK 🚨"
response = requests.post(WEBHOOK_URL, json={"content": test_message})
print(f"Test status: {response.status_code}")
    if direct_matches:
        best = sorted(direct_matches, key=lambda x: x["price"])[0]
        message = (
            "✈️ GANGA DETECTADA\n"
            "Ruta: Lima → Buenos Aires\n"
            "Tipo: DIRECTO\n"
            f"Precio: USD {best['price']}\n"
            f"Duración: {best['duration_h']:.2f} h\n"
            f"Límite configurado: USD {MAX_PRICE}\n"
            f"🔗 Ver vuelo: {URL}"
        )
        print(message)
        response = requests.post(WEBHOOK_URL, json={"content": message})
        print(f"Discord status: {response.status_code}")
        print(response.text[:500])

    elif one_stop_matches:
        best = sorted(one_stop_matches, key=lambda x: x["price"])[0]
        message = (
            "✈️ GANGA DETECTADA\n"
            "Ruta: Lima → Buenos Aires\n"
            "Tipo: 1 ESCALA\n"
            f"Precio: USD {best['price']}\n"
            f"Duración: {best['duration_h']:.2f} h\n"
            f"Límite configurado: USD {MAX_PRICE}\n"
            f"🔗 Ver vuelo: {URL}"
        )
        print(message)
        response = requests.post(WEBHOOK_URL, json={"content": message})
        print(f"Discord status: {response.status_code}")
        print(response.text[:500])

    else:
        print("No hay coincidencias válidas. No se envía alerta.")

    print("Fin del proceso.")
    browser.close()