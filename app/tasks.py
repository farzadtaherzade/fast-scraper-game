from sqlmodel import Session
from .database import engine
from .scrapers.scraper import scrape_gamespot_rss

def refresh_gamespot_rss_articles():
    scrape_gamespot_rss()

