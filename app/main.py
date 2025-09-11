from fastapi import FastAPI, BackgroundTasks
from sqlmodel import select
from .database import engine, create_db_and_tables, SessionDep
from app.scrapers.scraper import scrape_gamespot_rss 
from .models import Article

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    scrape_gamespot_rss()
    

@app.get("/")
def get_news(session: SessionDep) -> list[Article]:
    statment = select(Article).limit(20)
    return session.exec(statment).all()

@app.get("/refresh")
def refresh_news(background_tasks: BackgroundTasks) -> str:
    background_tasks.add_task(scrape_gamespot_rss)
    return "tasdk is running to refresh the article"
