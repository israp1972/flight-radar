import os
import re
import requests
from playwright.sync_api import sync_playwright
from routes_config import ROUTES

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# URL actual que ya funciona para Buenos Aires.
DEFAULT_ROUTE_URLS = {
    "LIM-BUE": "https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI2LTA1LTEyagwIAhIIL20vMGxwZmhyBwgBEgNFWkUaIxIKMjAyNi0wNS0xOGoHCAESA0VaRXIMCAISCC9tLzBscGZoQAFIAXABggELCP___________wGYAQE&hl=en&curr=USD",
}


def parse_duration_hours(text: str):
    m = re.search(r"(\d+)\s*hr(?:\s*(\d+)\s*min)?", text.lower())
    if not m:
        return None
    hours = int(m.group(1))
    minutes = int(m.group(2)) if m.group(2) else 0
    return hours + minutes / 60.0


def parse_flights_from_text(text: str):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    start_index = None
    end_index = None

    for i, line in enumerate(lines):
        low = line.lower()
        if (
            "top departing flights" in low
            or "mejores vuelos de ida" in low
            or "vuelos de ida" in low
        ):
            start_index = i
            break

    if start_index is None:
        return None

    for i in range(start_index + 1, len(lines)):
        line = lines[i]
        low = line.lower()
        if (
            low.startswith("price insights")
            or low.startswith("price history")
            or low.startswith("return flights")
            or low.startswith("información sobre precios")
            or low.startswith("historial de precios")
            or low.startswith("vuelos de regreso")
        ):
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
            if re.fullmatch(r"\$\d[\d,]*", line):
                if current:
                    has_duration = any("hr" in x.lower() for x in current)
                    has_stop = any(
                        ("nonstop" in x.lower())
                        or ("directo" in x.lower())
                        or ("1 stop" in x.lower())
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

        if re.fullmatch(r"\$\d[\d,]*", line):
            current.append(line)

            has_duration = any("hr" in x.lower() for x in current)
            has_stop = any(
                ("nonstop" in x.lower())
                or ("directo" in x.lower())
                or ("1 stop" in x.lower())
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
                if "nonstop" in low or "directo" in low:
                    stop_type = "direct"
                elif "1 stop" in low:
                    stop_type = "1_stop"

        if price is not None and duration_h is not None and stop_type is not None:
            parsed.append(
                {
                    "price": price,
                    "duration_h": duration_h,
                    "stop_type": stop_type,
                }
            )

    return parsed


def build_message(route_name: str, url: str, best: dict, flight_type: str):
    return (
        "✈️ GANGA DETECTADA\n"
        f"Ruta: Lima → {route_name}\n"
        f"Tipo: {flight_type}\n"
        f"Precio: USD {best['price']}\n"
        f"Duración: {best['duration_h']:.2f} h\n"
        f"🔗 {url}"
    )


def send_discord_alert(message: str):
    if not WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URL no está configurado. No se envió alerta.")
        return

    print("Enviando alerta a Discord...")
    requests.post(
        WEBHOOK_URL,
        json={"content": "@everyone 🚨 GANGA DETECTADA 🚨\n" + message},
        timeout=30,
    )


def process_route(page, route: dict):
    route_name = route["name"]
    route_code = route["code"]
    url = route.get("url") or DEFAULT_ROUTE_URLS.get(route_code, "")

    max_price = route["max_price"]
    max_duration_one_stop_hours = route["max_duration_one_stop_hours"]

    print(f"\n=== PROCESANDO RUTA: {route_name} ({route_code}) ===")

    if not url:
        print("Ruta omitida: no tiene URL configurada.")
        return

    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(12000)

        text = page.locator("body").inner_text()
        parsed = parse_flights_from_text(text)

        if parsed is None:
            print("No se encontró la sección de vuelos.")
            return

        direct_matches = [
            f
            for f in parsed
            if f["stop_type"] == "direct" and f["price"] <= max_price
        ]

        one_stop_matches = []
        if max_duration_one_stop_hours > 0:
            one_stop_matches = [
                f
                for f in parsed
                if f["stop_type"] == "1_stop"
                and f["price"] <= max_price
                and f["duration_h"] <= max_duration_one_stop_hours
            ]

        print("=== VUELOS PARSEADOS ===")
        for flight in parsed[:10]:
            print(flight)

        print("=== RESUMEN ===")
        print(f"Directos válidos: {len(direct_matches)}")
        print(f"1 escala válidos: {len(one_stop_matches)}")

        message = None

        if direct_matches:
            best = sorted(direct_matches, key=lambda x: x["price"])[0]
            message = build_message(route_name, url, best, "DIRECTO")
        elif one_stop_matches:
            best = sorted(one_stop_matches, key=lambda x: x["price"])[0]
            message = build_message(route_name, url, best, "1 ESCALA")

        if message:
            send_discord_alert(message)
        else:
            print("No hay coincidencias válidas.")

    except Exception as e:
        print(f"Error procesando {route_name}: {e}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for route in ROUTES:
            process_route(page, route)

        print("\nFin del proceso.")
        browser.close()


if __name__ == "__main__":
    main()