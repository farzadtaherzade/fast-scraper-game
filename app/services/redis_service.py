from app.database import redis_conn as redis
import json
from datetime import datetime, date 

def cache_articles(articles):
    serialized = []
    for article in articles:
        d = article.dict()
        for key, value in d.items():
            if isinstance(value, (datetime, date)):
                d[key] = value.isoformat()  # convert datetime to string
        serialized.append(d)

    redis.set("articles", json.dumps(serialized), ex=10800)

def get_cache_article():
    return redis.get("articles")
