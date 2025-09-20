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

feeds = [
    {
        "source": "GAMESPOT",
        "url": "https://www.gamespot.com/feeds/game-news",
    },
    {
        "source": "IGN",
        "url": "https://feeds.ign.com/ign/games-all",
    }
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
                format_string = "%a, %d %b %Y %H:%M:%S %z"
                published_at = datetime.strptime(item.pubDate.text, format_string) # type: ignore
                description = item.description.text # type: ignore
                url = item.link.text # type: ignore

            
                article = Article(title=title, published_date=published_at, description=description, url=url, source=feed["source"])
    
                statment = select(Article).where(Article.url == url)
            
                if not session.exec(statment).first():
                    session.add(article)
                    message = (
                        f"🎮 *{article.title}*\n"
                        f"🌐 Source: _{article.source}_\n"
                        f"📅 Published: {article.published_date.strftime('%Y-%m-%d %H:%M')}\n"
                        f"🔗 [Read more]({article.url})\n\n"
                        f"📝 *Summary:*\n{article.description[:501]}{'...' if len(article.description) > 500 else ''}"
                    )

                    q.enqueue(send_news_message,message, "Markdown")

            q.enqueue(cached_article_data)
            session.commit()

    
    print("finished")
    return "finiseh"
