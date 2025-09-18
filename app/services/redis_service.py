from app.database import redis_conn as redis

def cache_articles(articles):
    redis.set("articles", articles, ex=10800)
    return True

def get_cache_article():
    return redis.get("articles")
