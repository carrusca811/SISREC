import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

if not MONGO_URI:
    raise Exception("MONGO_URI is not set in .env")

if not MONGO_DB:
    raise Exception("MONGO_DB is not set in .env")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

# Coleções
movies_collection = db["movies"]
users_collection = db["users"]
reviews_collection = db["reviews"]