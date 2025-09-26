from fastapi import FastAPI, BackgroundTasks
from .database import create_db_and_tables, SessionDep, redis_conn
from app.scrapers.scraper import scrape_games_rss 
from .models import Article
from rq import Queue
from rq_scheduler import Scheduler
from datetime import timedelta, datetime
from app.tasks import cached_article_data
from app.services.redis_service import get_cache_article 
from typing import Optional

app = FastAPI()

q = Queue(connection=redis_conn)
scheduler = Scheduler(connection=redis_conn)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=cached_article_data,
            interval=7200,
            repeat=None,
            )

    scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=scrape_games_rss, 
            interval=3600,
            repeat=None,
            )
@app.get("/")
def get_news(session: SessionDep) -> Optional[list[Article]]:
    return get_cache_article()

@app.get("/refresh")
def refresh_news(background_tasks: BackgroundTasks) -> str:
    background_tasks.add_task(scrape_games_rss)
    return "task is running to refresh the article"
