import os

from dotenv import load_dotenv
from pymongo.asynchronous.mongo_client import AsyncMongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DB_NAME")

client = AsyncMongoClient(MONGO_URI)

database = client[DATABASE_NAME]