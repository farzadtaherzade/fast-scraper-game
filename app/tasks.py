from app.services.redis_service import cache_articles
from app.models import Article
from sqlmodel import Session, select
from datetime import date, datetime
from app.database import engine

"""
caching the article every 2 hours
"""
def cached_article_data():
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
   
    with Session(engine) as session:
        statment = select(Article).where(Article.created_at >= start_of_day, Article.created_at <= end_of_day) # type: ignore
        cache_articles(session.exec(statment).all())
