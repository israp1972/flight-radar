import subprocess
import json

ROUTES = [
    ("LIM", "BUE"),
    ("LIM", "MIA"),
    ("LIM", "MAD"),
]

results = []

def run_route(origin, destination):
    print(f"\n=== {origin} → {destination} ===")

    subprocess.run(["python", "collect_prices_dynamic.py", origin, destination])

    try:
        with open("price_history.json", "r") as f:
            data = json.load(f)
    except:
        return None

    last_snapshot = data[-1]
    prices = [f["price"] for f in last_snapshot.get("flights", []) if f.get("price")]

    if not prices:
        return None

    current_min = min(prices)

    all_prices = []
    for snap in data:
        for f in snap.get("flights", []):
            if f.get("price"):
                all_prices.append(f["price"])

    if not all_prices:
        return None

    historical_min = min(all_prices)

    ratio = current_min / historical_min

    if ratio <= 1.0:
        score = 100
    elif ratio <= 1.05:
        score = 90
    elif ratio <= 1.10:
        score = 80
    elif ratio <= 1.20:
        score = 60
    else:
        score = 30

    return {
        "route": f"{origin}->{destination}",
        "price": current_min,
        "score": score
    }

def main():
    for origin, destination in ROUTES:
        result = run_route(origin, destination)
        if result:
            results.append(result)

    if not results:
        print("No hay datos.")
        return

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    print("\n=== TOP OPORTUNIDADES ===")
    for r in ranked:
        print(f"{r['route']} | ${r['price']} | score {r['score']}")

if __name__ == "__main__":
    main()