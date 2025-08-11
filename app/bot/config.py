import os

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TG_BOT_TOKEN")
DATA_FILE = "data/reminders.json"