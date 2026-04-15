from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
TARGET_CHAT_IDS = [
    int(x) for x in os.getenv("TARGET_CHAT_IDS").split(",")
]

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
