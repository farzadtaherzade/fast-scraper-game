# FastAPI app
web: uvicorn app.main:app --host 0.0.0.0 --port 10000

# RQ worker
worker: rq worker --url $REDIS_URL

# RQ scheduler
scheduler: rqscheduler --url $REDIS_URL

