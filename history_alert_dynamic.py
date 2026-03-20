import subprocess
import json
import os
import requests
from price_history import get_min_price_ever

def calculate_score(current, historical):
    if historical == 0:
        return 0

    ratio = current / historical

    if ratio <= 1.0:
        return 100
    elif ratio <= 1.05:
        return 90
    elif ratio <= 1.10:
        return 80
    elif ratio <= 1.20:
        return 60
    elif ratio <= 1.30:
        return 40
    else:
        return 10

def calculate_average_price(history_data):
    prices = []

    for snap in history_data:
        for f in snap.get("flights", []):
            if f.get("price"):
                prices.append(f["price"])

    if not prices:
        return None

    return sum(prices) / len(prices)

def run(origin, destination):
    print(f"=== HISTORY ALERT {origin} → {destination} ===")

    subprocess.run(["python", "collect_prices_dynamic.py", origin, destination])

    try:
        with open("price_history.json", "r") as f:
            data = json.load(f)
    except:
        print("No se pudo leer el histórico.")
        return

    last_snapshot = data[-1]
    prices = [f["price"] for f in last_snapshot.get("flights", []) if f.get("price")]

    if not prices:
        print("No hay precios.")
        return

    current_min = min(prices)
    historical_min = get_min_price_ever()
    average_price = calculate_average_price(data)

    score = calculate_score(current_min, historical_min)

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL") or "https://discord.com/api/webhooks/1483789945079333014/ZF_mb7h-A3q9Vr681SpL0YVal-vHIeOxXuXcAoQI1Jgub7y5v5s8IWoAwJHuBp8qhfyY"

    anomaly_threshold = average_price * 0.75

    message = None

    if current_min < anomaly_threshold:
        message = f"🚨 GANGA DETECTADA {origin}->{destination}\n${current_min} vs avg ${round(average_price,2)}"
    elif score >= 90:
        message = f"🔥 EXCELENTE {origin}->{destination}\n${current_min} score {score}"
    elif score >= 80:
        message = f"🟢 BUENA {origin}->{destination}\n${current_min} score {score}"

    if message:
        print(message)
        requests.post(webhook_url, json={"content": message})
    else:
        print("Sin oportunidad")

import sys

if __name__ == "__main__":
    if len(sys.argv) == 3:
        run(sys.argv[1], sys.argv[2])
    else:
        print("Uso: python history_alert_dynamic.py LIM BUE")