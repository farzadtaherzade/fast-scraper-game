from app.database import redis_conn as redis
import json
from datetime import datetime, date 

_memory_articles = []


def cache_articles(articles):
    global _memory_articles
    serialized = []
    for article in articles:
        # Ensure we work with dict
        d = article.dict() if hasattr(article, "dict") else dict(article)
        for k, v in d.items():
            if isinstance(v, (datetime, date)):
                d[k] = v.isoformat()
        serialized.append(d)

    _memory_articles = serialized
    try:
        redis.set("articles", json.dumps(serialized), ex=10800)
    except Exception as exc:
        print(f"[cache] Redis unavailable, using memory cache: {exc}")


def get_cache_article():
    try:
        data = redis.get("articles")
        if data is not None:
            return json.loads(data)
    except Exception as exc:
        print(f"[cache] Redis unavailable, using memory cache: {exc}")
    return _memory_articles
