import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlmodel import select, Session
from app.models import Article
from app.database import engine

GAMESPOT_RSS_URL = "https://www.gamespot.com/feeds/mashup"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def scrape_gamespot_rss():
    response = requests.get(GAMESPOT_RSS_URL, headers=headers, timeout=30)

    soup = BeautifulSoup(response.content, "xml")

    session = Session(engine)

    for item in soup.find_all("item"):
        title = item.title.text
        format_string = "%a, %d %b %Y %H:%M:%S %z"
        published_at = datetime.strptime(item.pubDate.text, format_string)
        description = item.description.text
        url = item.link.text

        # print(title[:10], url, published_at, url)
        
        article = Article(title=title, published_date=published_at, description=description, url=url, source="GAMESPOT")
 
        statment = select(Article).where(Article.title == title)
        
        if not session.exec(statment).first():
            session.add(article)


    session.commit()
    return "finiseh"

# scrape_gamespot_rss()
