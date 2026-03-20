from price_history import add_snapshot, get_min_price_ever

test_flights = [
    {"price": 346, "duration_h": 4.3, "stop_type": "direct"},
    {"price": 429, "duration_h": 10.6, "stop_type": "1_stop"}
]

add_snapshot(test_flights)

min_price = get_min_price_ever()

print("Precio mínimo histórico:", min_price)