from price_history import PriceHistory

history = PriceHistory()

key = history.record_price(
    origin="LIM",
    destination="EZE",
    depart_date="2026-05-10",
    return_date="2026-05-17",
    price=155,
    stops="direct",
    duration_hours=4.3,
    airline="Latam",
)

print("KEY:", key)
print(history.get_summary(key))

key = history.record_price(
    origin="LIM",
    destination="EZE",
    depart_date="2026-05-10",
    return_date="2026-05-17",
    price=142,
    stops="direct",
    duration_hours=4.3,
    airline="Latam",
)

print(history.get_summary(key))