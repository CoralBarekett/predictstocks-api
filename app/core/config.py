import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    GOOGLE_NEWS_API_KEY = os.getenv("GOOGLE_NEWS_API_KEY")

    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

settings = Settings()