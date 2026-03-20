import os
import re
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

URL = "https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI2LTA1LTEyagwIAhIIL20vMGxwZmhyBwgBEgNFWkUaIxIKMjAyNi0wNS0xOGoHCAESA0VaRXIMCAISCC9tLzBscGZoQAFIAXABggELCP___________wGYAQE&hl=en&curr=USD"

MAX_PRICE = 186
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
    page.wait_for_timeout(12000)

    text = page.locator("body").inner_text()
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    start_index = None
    end_index = None

    for i, line in enumerate(lines):
        if "Top departing flights" in line:
            start_index = i
            break

    if start_index is None:
        print("No se encontró la sección de vuelos.")
        browser.close()
        raise SystemExit

    for i in range(start_index + 1, len(lines)):
        line = lines[i]
        if line.startswith("Price insights") or line.startswith("Price history") or line.startswith("Return flights"):
            end_index = i
            break

    if end_index is None:
        end_index = min(len(lines), start_index + 120)

    section = lines[start_index:end_index]

    flights = []
    current = []
    seen_first_real_flight = False

    for line in section:
        if not seen_first_real_flight:
            # Ignorar banners/resúmenes hasta encontrar un vuelo real
            if re.fullmatch(r"\$\d[\d,]*", line):
                if current:
                    has_duration = any("hr" in x.lower() for x in current)
                    has_stop = any(
                        ("nonstop" in x.lower()) or ("1 stop" in x.lower())
                        for x in current
                    )
                    if has_duration and has_stop:
                        current.append(line)
                        flights.append(current)
                        current = []
                        seen_first_real_flight = True
                    else:
                        current = []
                else:
                    current = []
            else:
                current.append(line)
            continue

        # Después del primer vuelo real, seguimos agrupando normalmente
        if re.fullmatch(r"\$\d[\d,]*", line):
            current.append(line)

            has_duration = any("hr" in x.lower() for x in current)
            has_stop = any(
                ("nonstop" in x.lower()) or ("1 stop" in x.lower())
                for x in current
            )

            if has_duration and has_stop:
                flights.append(current)

            current = []
        else:
            current.append(line)

    parsed = []

    for block in flights:
        price = None
        duration_h = None
        stop_type = None

        for line in block:
            if price is None and re.fullmatch(r"\$\d[\d,]*", line):
                price = int(line.replace("$", "").replace(",", ""))

            if duration_h is None and "hr" in line.lower():
                parsed_duration = parse_duration_hours(line)
                if parsed_duration is not None:
                    duration_h = parsed_duration

            low = line.lower()
            if stop_type is None:
                if "nonstop" in low:
                    stop_type = "direct"
                elif "1 stop" in low:
                    stop_type = "1_stop"

        if price is not None and duration_h is not None and stop_type is not None:
            parsed.append({
                "price": price,
                "duration_h": duration_h,
                "stop_type": stop_type
            })

    direct_matches = [
        f for f in parsed
        if f["stop_type"] == "direct" and f["price"] <= MAX_PRICE
    ]

    one_stop_matches = [
        f for f in parsed
        if f["stop_type"] == "1_stop"
        and f["price"] <= MAX_PRICE
        and f["duration_h"] <= MAX_DURATION_ONE_STOP_HOURS
    ]

    print("=== VUELOS PARSEADOS ===")
    for f in parsed[:10]:
        print(f)

    print("=== RESUMEN ===")
    print(f"Directos válidos: {len(direct_matches)}")
    print(f"1 escala válidos: {len(one_stop_matches)}")

    message = None

    if direct_matches:
        best = sorted(direct_matches, key=lambda x: x["price"])[0]
        message = (
            "✈️ GANGA DETECTADA\n"
            "Ruta: Lima → Buenos Aires\n"
            "Tipo: DIRECTO\n"
            f"Precio: USD {best['price']}\n"
            f"Duración: {best['duration_h']:.2f} h\n"
            f"🔗 {URL}"
        )

    elif one_stop_matches:
        best = sorted(one_stop_matches, key=lambda x: x["price"])[0]
        message = (
            "✈️ GANGA DETECTADA\n"
            "Ruta: Lima → Buenos Aires\n"
            "Tipo: 1 ESCALA\n"
            f"Precio: USD {best['price']}\n"
            f"Duración: {best['duration_h']:.2f} h\n"
            f"🔗 {URL}"
        )

    if message:
        print("Enviando alerta a Discord...")
        requests.post(
            WEBHOOK_URL,
            json={"content": "@everyone 🚨 GANGA DETECTADA 🚨\n" + message}
        )
    else:
        print("No hay coincidencias válidas.")

    print("Fin del proceso.")
    browser.close()