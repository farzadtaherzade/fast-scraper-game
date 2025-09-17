from fastapi import FastAPI, BackgroundTasks, Depends
from sqlmodel import select
from .database import engine, create_db_and_tables, SessionDep, redis_conn
from app.scrapers.scraper import scrape_gamespot_rss 
from .models import Article
from rq import Queue

app = FastAPI()

q = Queue(connection=redis_conn)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    q.enqueue(scrape_gamespot_rss)

@app.get("/")
def get_news(session: SessionDep) -> list[Article]:
    count = len(session.exec(select(Article)).all())

    statment = select(Article).offset(count - 20).limit(20)
    return session.exec(statment).all()

@app.get("/refresh")
def refresh_news(background_tasks: BackgroundTasks) -> str:
    background_tasks.add_task(scrape_gamespot_rss)
    return "task is running to refresh the article"
