import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlmodel import select, Session
from app.models import Article
from app.database import engine, redis_conn
from app.services.telegram_service import send_news_message 
from app.tasks import cached_article_data
from rq import Queue

GAMESPOT_RSS_URL = "https://www.gamespot.com/feeds/mashup"
IGN_RSS_GAME_ARTICLE_URL = ""
IGN_RSS_GAME_REVIEW_URL = ""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

q = Queue(connection=redis_conn)

def print_hello_world():
    print("hello world")

def scrape_gamespot_rss():
    response = requests.get(GAMESPOT_RSS_URL, headers=headers, timeout=30)

    soup = BeautifulSoup(response.content, "xml")
    with Session(engine) as session: 

        for item in soup.find_all("item"):
            title = item.title.text
            format_string = "%a, %d %b %Y %H:%M:%S %z"
            published_at = datetime.strptime(item.pubDate.text, format_string)
            description = item.description.text
            url = item.link.text

        
            article = Article(title=title, published_date=published_at, description=description, url=url, source="GAMESPOT")
 
            statment = select(Article).where(Article.url == url)
         
            if not session.exec(statment).first():
                session.add(article)
                message = (
                    f"🎮 *{title}*\n"
                    f"📅 Published on: {published_at}\n"
                    f"🔗 Read more: {url}\n\n"
                    f"📝 *Description:*\n{description[:25]}\n"
                )

                q.enqueue(send_news_message,message, "Markdown")

        q.enqueue(cached_article_data)
        session.commit()
    print("finished")
    return "finiseh"

# scrape_gamespot_rss()
