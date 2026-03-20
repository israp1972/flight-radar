from price_history import load_history, get_min_price_ever

history = load_history()

print(f"Snapshots totales: {len(history)}")

if not history:
    print("No hay histórico.")
    raise SystemExit

last_snapshot = history[-1]
last_flights = last_snapshot["flights"]

print("=== ÚLTIMO SNAPSHOT ===")
for f in last_flights:
    print(f)

min_price_ever = get_min_price_ever()
print(f"\nMÍNIMO HISTÓRICO GLOBAL: {min_price_ever}")

current_min = min(f["price"] for f in last_flights) if last_flights else None
print(f"MÍNIMO ACTUAL: {current_min}")

if current_min is not None and min_price_ever is not None:
    if current_min <= min_price_ever:
        print("ALERTA: el precio actual es mínimo histórico.")
    else:
        diff = current_min - min_price_ever
        print(f"No es mínimo histórico. Diferencia: +{diff}")