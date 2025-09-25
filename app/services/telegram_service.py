import requests
from dotenv import load_dotenv
import os

load_dotenv(".env")

bot_token = os.getenv("BOT_TOKEN")
channel_id = os.getenv("CHANNEL_ID")

def send_news_message(text: str, parse_mode):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
            "text": text,
            "chat_id": channel_id,
            "parse_mode": parse_mode
            }
    res = requests.post(
            url,
            json=payload
            )
    return "message sended"
