import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(str(Path(".bot.env").resolve()))
load_dotenv(str(Path(".db.env").resolve()))

VK_API_KEY = os.getenv("VK_API_KEY", "")
DOG_API_KEY = os.getenv("DOG_API_KEY", "")
DOG_API_PROVIDER_URL = os.getenv("DOG_API_PROVIDER_URL", "https://api.thedogapi.com/")

SQLALCHEMY_DATABASE_URI = (
    f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}'
    f'@db/{os.getenv("POSTGRES_DB")}'
)
