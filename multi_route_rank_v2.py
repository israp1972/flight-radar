import subprocess
from price_history_route import get_route_prices

ROUTES = [
    ("LIM", "BUE"),
    ("LIM", "MIA"),
    ("LIM", "MAD"),
]

results = []

def calculate_score(current, prices):
    if not prices:
        return 0

    avg = sum(prices) / len(prices)
    ratio = current / avg

    if ratio <= 0.75:
        return 100  # ganga real
    elif ratio <= 0.85:
        return 90
    elif ratio <= 0.95:
        return 80
    elif ratio <= 1.10:
        return 60
    else:
        return 30

def run_route(origin, destination):
    route_key = f"{origin}-{destination}"

    print(f"\n=== {route_key} ===")

    subprocess.run(["python", "collect_prices_dynamic.py", origin, destination])

    prices = get_route_prices(route_key)

    if not prices:
        return None

    current_min = min(prices[-5:])  # últimos datos
    historical_min = min(prices)

    score = calculate_score(current_min, prices)

    return {
        "route": route_key,
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

    print("\n=== TOP OPORTUNIDADES (REAL) ===")
    for r in ranked:
        print(f"{r['route']} | ${r['price']} | score {r['score']}")

if __name__ == "__main__":
    main()