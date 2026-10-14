import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


def send_news_message(text: str, parse_mode: str = "Markdown") -> str:
    if not BOT_TOKEN or not CHANNEL_ID:
        raise RuntimeError("Telegram is not configured")
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"text": text[:4096], "chat_id": CHANNEL_ID, "parse_mode": parse_mode},
        timeout=20,
    )
    response.raise_for_status()
    return "Message sent to Telegram"


def send_latest_news(articles: list[dict]) -> str:
    if not articles:
        return "No cached stories to send"
    sent = 0
    for article in articles[:10]:
        message = (f"*{article.get('title', 'Game news')}*\n"
                   f"Source: _#{article.get('source', 'games')}_\n"
                   f"[Read more]({article.get('url', '')})")
        send_news_message(message)
        sent += 1
    return f"Sent {sent} latest stories to Telegram"
