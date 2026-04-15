from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))
