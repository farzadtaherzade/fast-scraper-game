from app.database import redis_conn as redis
import json
from datetime import datetime, date 

def cache_articles(articles):
    serialized = []
    for article in articles:
        # Ensure we work with dict
        d = article.dict() if hasattr(article, "dict") else dict(article)
        for k, v in d.items():
            if isinstance(v, (datetime, date)):
                d[k] = v.isoformat()
        serialized.append(d)

    redis.set("articles", json.dumps(serialized), ex=10800)

def get_cache_article():
    data = redis.get("articles")
    if data is None:
        return []
    return json.loads(data)
