from fastapi import FastAPI, BackgroundTasks
from sqlmodel import select
from .database import create_db_and_tables, SessionDep, redis_conn
from app.scrapers.scraper import scrape_gamespot_rss 
from .models import Article
from rq import Queue
from rq_scheduler import Scheduler
from datetime import timedelta, datetime
from app.tasks import cached_article_data

app = FastAPI()

q = Queue(connection=redis_conn)
scheduler = Scheduler(connection=redis_conn)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    scheduler.schedule(
            scheduled_time=datetime.utcnow() + timedelta(hours=2),
            func=cached_article_data,
            interval=7200,
            repeat=None,
            )

    scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=scrape_gamespot_rss, 
            interval=3600,
            repeat=None,
            )
    jobs = list(scheduler.get_jobs())
    print(jobs)
@app.get("/")
def get_news(session: SessionDep) -> list[Article]:
    count = len(session.exec(select(Article)).all())

    statment = select(Article).offset(count - 20).limit(20)
    return session.exec(statment).all()

@app.get("/refresh")
def refresh_news(background_tasks: BackgroundTasks) -> str:
    background_tasks.add_task(scrape_gamespot_rss)
    return "task is running to refresh the article"
