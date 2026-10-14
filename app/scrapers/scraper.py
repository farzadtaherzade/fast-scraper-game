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
        "source": "DEV.to",
        "url": "https://dev.to/feed"
    },
    {
        "source": "GAME_INFORMER",
        "url": "https://gameinformer.com/news.xml"
    },
    {
        "source": "POLYGON",
        "url": "https://polygon.com/rss/index.xml"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

q = Queue(connection=redis_conn)

def scrape_games_rss():
    new_count = 0
    for feed in feeds:
        try:
            response = requests.get(feed["url"], headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"[scraper] {feed['source']} unavailable: {exc}")
            continue

        soup = BeautifulSoup(response.content, "xml")
        with Session(engine) as session:
            for item in soup.find_all("item"):
                title_node = item.find("title")
                url_node = item.find("link")
                date_node = item.find("pubDate")
                if not title_node or not url_node or not date_node:
                    continue
                title = title_node.get_text(strip=True)
                description = item.find("description")
                description_text = description.get_text(" ", strip=True) if description else ""
                url = url_node.get_text(strip=True)
                date_str = date_node.get_text(strip=True)
                published_at = parser.parse(date_str)

                # Normalize to UTC
                if published_at.tzinfo:
                    published_at = published_at.astimezone(pytz.UTC)
                else:
                    published_at = published_at.replace(tzinfo=pytz.UTC)
            
                article = Article(title=title, published_date=published_at, description=description_text, url=url, source=feed["source"])
    
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

                    q.enqueue(send_news_message,message, "Markdown")

            q.enqueue(cached_article_data)
            session.commit()

    
    print("finished")
    return "finiseh"
