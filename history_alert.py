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

def run_history_alert():
    print("=== HISTORY ALERT ===")

    subprocess.run(["python", "collect_prices.py"])

    try:
        with open("price_history.json", "r") as f:
            data = json.load(f)
    except:
        print("No se pudo leer el histórico.")
        return

    if not data:
        print("Histórico vacío.")
        return

    last_snapshot = data[-1]
    prices = [f["price"] for f in last_snapshot.get("flights", []) if f.get("price")]

    if not prices:
        print("No hay precios en el último snapshot.")
        return

    current_min = min(prices)
    print(f"MÍNIMO ACTUAL: {current_min}")

    historical_min = get_min_price_ever()
    print(f"MÍNIMO HISTÓRICO: {historical_min}")

    average_price = calculate_average_price(data)
    print(f"PROMEDIO HISTÓRICO: {round(average_price, 2) if average_price else 'N/A'}")

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL") or "https://discord.com/api/webhooks/1483789945079333014/ZF_mb7h-A3q9Vr681SpL0YVal-vHIeOxXuXcAoQI1Jgub7y5v5s8IWoAwJHuBp8qhfyY"

    if historical_min is None or average_price is None:
        print("Datos insuficientes.")
        return

    score = calculate_score(current_min, historical_min)
    print(f"SCORE: {score}/100")

    # 🚨 DETECCIÓN DE PRECIO ANORMAL
    anomaly_threshold = average_price * 0.75  # 25% más barato que promedio

    message = None

    if current_min < anomaly_threshold:
        message = (
            f"🚨 ERROR / GANGA DETECTADA\n"
            f"Precio: ${current_min}\n"
            f"Promedio: ${round(average_price,2)}\n"
            f"Histórico: ${historical_min}\n"
            f"Score: {score}/100"
        )
    elif score >= 90:
        message = (
            f"🔥 OFERTA EXCELENTE\n"
            f"Precio: ${current_min}\n"
            f"Histórico: ${historical_min}\n"
            f"Score: {score}/100"
        )
    elif score >= 80:
        message = (
            f"🟢 BUENA OFERTA\n"
            f"Precio: ${current_min}\n"
            f"Histórico: ${historical_min}\n"
            f"Score: {score}/100"
        )

    if message:
        print(message)

        try:
            requests.post(webhook_url, json={"content": message})
            print("Alerta enviada a Discord")
        except:
            print("Error enviando a Discord")
    else:
        print("Sin oportunidad relevante")

if __name__ == "__main__":
    run_history_alert()