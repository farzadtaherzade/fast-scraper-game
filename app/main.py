from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from .database import create_db_and_tables, redis_conn
from app.scrapers.scraper import scrape_games_rss
from app.services.redis_service import get_cache_article
from app.services.telegram_service import send_latest_news

app = FastAPI(title="GamePulse API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(Path(__file__).parent / "templates" / "index.html")

@app.get("/api/articles")
def articles():
    return get_cache_article()

@app.post("/api/refresh")
def refresh_news(background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_games_rss)
    return {"message": "Refresh started. New stories will appear shortly."}

@app.post("/api/telegram/send")
def send_to_telegram():
    return {"message": send_latest_news(get_cache_article())}

@app.get("/health")
def health():
    try:
        redis_conn.ping()
        return {"status": "ok", "redis": "connected"}
    except Exception:
        return {"status": "degraded", "redis": "unavailable"}
