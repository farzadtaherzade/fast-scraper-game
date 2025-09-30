import requests
from bs4 import BeautifulSoup
from dateutil import parser
from sqlmodel import select, Session
from app.models import Article
from app.database import engine, redis_conn
from app.services.telegram_service import send_news_message 
from app.tasks import cached_article_data
from rq import Queue
import pytz

GAMESPOT_RSS_URL = "https://www.gamespot.com/feeds/mashup"

feeds = [
    {
        "source": "GAMESPOT",
        "url": "https://www.gamespot.com/feeds/game-news",
    },
    {
        "source": "IGN",
        "url": "https://feeds.ign.com/ign/games-all",
    },
    {
        "source": "GAME_INFORMER",
        "url": "https://gameinformer.com/news.xml",
    },
    {
        "source": "POLYGON",
        "url": "https://polygon.com/rss/index.xml",
    },
    {
        "source": "DEV_PYTHON",
        "url": "https://dev.to/feed/tag/python",
    },
    {
        "source": "DEV_WEBDEV",
        "url": "https://dev.to/feed/tag/webdev",
    },
    {
        "source": "DEV_GAMEDEV",
        "url": "https://dev.to/feed/tag/gamedev",
    },
    {
        "source": "DEV_DATABASE",
        "url": "https://dev.to/feed/tag/database",
    },
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

q = Queue(connection=redis_conn)

def scrape_games_rss():

    for feed in feeds:
        response = requests.get(feed["url"], headers=headers, timeout=30)

        soup = BeautifulSoup(response.content, "xml")
        with Session(engine) as session: 
            for item in soup.find_all("item"):
                title = item.title.text # type: ignore
                description = item.description.text # type: ignore
                url = item.link.text # type: ignore

                date_str = item.pubDate.text  # e.g. "Tue, 23 Sep 2025 19:50:40 GMT"
                published_at = parser.parse(date_str)  # this returns datetime

                # Normalize to UTC
                if published_at.tzinfo:
                    published_at = published_at.astimezone(pytz.UTC)
                else:
                    published_at = published_at.replace(tzinfo=pytz.UTC)
            
                article = Article(title=title, published_date=published_at, description=description, url=url, source=feed["source"])
    
                statment = select(Article).where(Article.url == url)
            
                if not session.exec(statment).first():
                    session.add(article)
                    message = (
                        f"🎮 *{article.title}*\n"
                        f"🌐 Source: _#{article.source}_\n"
                        f"📅 Published: {article.published_date.strftime('%Y-%m-%d %H:%M')}\n"
                        f"🔗 [Read more]({article.url})\n\n"
                        f"📝 *Summary:*\n{article.description[:501]}{'...' if len(article.description) > 500 else ''}"
                    )

                    send_news_message(message,"Markdown")

            cached_article_data()
            session.commit()

    
    print("finished")
    return "finiseh"
