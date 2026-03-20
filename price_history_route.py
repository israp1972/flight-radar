import json
import os
from datetime import datetime

FILE_PATH = "price_history_routes.json"

def load_history():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_snapshot(route, flights):
    history = load_history()

    snapshot = {
        "route": route,
        "timestamp": datetime.utcnow().isoformat(),
        "flights": flights
    }

    history.append(snapshot)
    save_history(history)

    print(f"[{route}] histórico actualizado ({len(history)})")

def get_route_prices(route):
    history = load_history()
    prices = []

    for snap in history:
        if snap.get("route") == route:
            for f in snap.get("flights", []):
                if f.get("price"):
                    prices.append(f["price"])

    return prices