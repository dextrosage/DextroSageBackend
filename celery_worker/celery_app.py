import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

redis_link = os.getenv("REDIS_URL")


celery_app = Celery(
    "backend",
    broker=redis_link,
    backend=redis_link,
    include=["celery_worker.tasks"]
)

celery_app.conf.update(
    broker_transport_options={
        "socket_connect_timeout": 2,   # seconds
        "socket_timeout": 2,
    }
)