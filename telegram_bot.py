import os
import django
import requests
import time
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "G_cake_studio.settings")
django.setup()

from django.contrib.auth.models import User
from g_cake_studio_app.models import TelegramAuthToken

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

offset = None

def send_message(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

print("Bot started...")

offset = None

while True:
    response = requests.get(
        f"{BASE_URL}/getUpdates",
        params={
            "offset": offset,
            "timeout": 30
        },
        timeout=35
    )

    data = response.json()

    for update in data.get("result", []):
        offset = update["update_id"] + 1

        message = update.get("message")
        if not message:
            continue

        text = message.get("text", "")
        chat = message.get("chat")
        user_id = chat.get("id")
        username = chat.get("username") or f"tg_{user_id}"

        print("TEXT:", text)

        if text.startswith("/start"):
            parts = text.split()

            start_param = None
            if len(parts) > 1:
                start_param = parts[1]

            user, created = User.objects.get_or_create(username=username)

            auth_token = TelegramAuthToken.objects.create(user=user)

            link = f"http://127.0.0.1:8000/check-telegram-auth/?token={auth_token.token}"

            if start_param == "register":
                send_message(user_id, f"Регистрация через Telegram:\n{link}")
            else:
                send_message(user_id, f"Вход через Telegram:\n{link}")

    time.sleep(2)

