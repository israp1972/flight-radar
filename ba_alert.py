import os
import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

print(f"WEBHOOK_URL cargado: {bool(WEBHOOK_URL)}")

test_response = requests.post(
    WEBHOOK_URL,
    json={"content": "🚨 TEST DESDE GITHUB ACTIONS 🚨"}
)

print(f"Discord status: {test_response.status_code}")
print(test_response.text[:200])
print("Prueba terminada")