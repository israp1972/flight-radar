import re
from playwright.sync_api import sync_playwright
from price_history import add_snapshot

URL = "https://www.google.com/travel/flights/search?tfs=CBwQAhojEgoyMDI2LTA1LTEyagwIAhIIL20vMGxwZmhyBwgBEgNFWkUaIxIKMjAyNi0wNS0xOGoHCAESA0VaRXIMCAISCC9tLzBscGZoQAFIAXABggELCP___________wGYAQE&hl=en&curr=USD"


def parse_duration_hours(text: str):
    m = re.search(r"(\d+)\s*hr(?:\s*(\d+)\s*min)?", text.lower())
    if not m:
        return None
    hours = int(m.group(1))
    minutes = int(m.group(2)) if m.group(2) else 0
    return hours + minutes / 60.0


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
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

    print("=== VUELOS PARSEADOS ===")
    for f in parsed[:10]:
        print(f)

    add_snapshot(parsed)

    print("Fin del proceso.")
    browser.close()