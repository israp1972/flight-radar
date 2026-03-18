import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1483789945079333014/ZF_mb7h-A3q9Vr681SpL0YVal-vHIeOxXuXcAoQI1Jgub7y5v5s8IWoAwJHuBp8qhfyY"

def send_alert(message):
    data = {
        "content": message
    }
    requests.post(WEBHOOK_URL, json=data)

send_alert("🚀 Radar funcionando correctamente")