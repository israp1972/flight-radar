import json
import os
from datetime import datetime

FILE_PATH = "price_history.json"


def load_history():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_snapshot(flights):
    history = load_history()

    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "flights": flights
    }

    history.append(snapshot)
    save_history(history)

    print(f"Histórico actualizado. Total snapshots: {len(history)}")


def get_last_prices():
    history = load_history()
    if not history:
        return []
    return history[-1]["flights"]


def get_min_price_ever():
    history = load_history()
    prices = []

    for snap in history:
        for f in snap["flights"]:
            if "price" in f:
                prices.append(f["price"])

    return min(prices) if prices else None