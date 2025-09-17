import requests
from dotenv import load_dotenv
import os
import json

load_dotenv('.local.env')

bot_token = os.getenv("BOT_TOKEN")
channel_id = os.getenv("CHANNEL_ID")
PROXY_URL = 'https://thingproxy.freeboard.io/fetch/'

def send_news_message(text: str, parse_mode):
    url = f"https:/api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
            "text": text,
            "chat_id": channel_id,
            "parse_mode": parse_mode
            }
    res = requests.post(
            PROXY_URL + url,
            headers={"Content-Type": "application/json"},
            data=payload
            )
    print(res.status_code)
    return "message sended"

    
