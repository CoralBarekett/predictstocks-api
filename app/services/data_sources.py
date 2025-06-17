import time
import httpx
import logging
from datetime import datetime, timedelta
from typing import List
from app.models.schemas import SocialMediaPost
from app.core.config import settings

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": settings.REDDIT_USER_AGENT}

async def fetch_reddit_posts(ticker: str) -> List[SocialMediaPost]:
    try:
        auth = httpx.BasicAuth(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET)
        async with httpx.AsyncClient(timeout=10) as client:
            token_resp = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data={
                    "grant_type": "password",
                    "username": settings.REDDIT_USERNAME,
                    "password": settings.REDDIT_PASSWORD
                },
                headers={"User-Agent": settings.REDDIT_USER_AGENT}
            )
            token = token_resp.json()["access_token"]
            headers = {
                "Authorization": f"bearer {token}",
                "User-Agent": settings.REDDIT_USER_AGENT
            }
            search_url = f"https://oauth.reddit.com/r/stocks/search.json?q={ticker}&restrict_sr=1&sort=new"
            resp = await client.get(search_url, headers=headers)
            data = resp.json()
            return [
                SocialMediaPost(
                    platform="reddit",
                    content=post["data"]["title"],
                    timestamp=datetime.utcfromtimestamp(post["data"]["created_utc"])
                )
                for post in data["data"]["children"]
            ][:10]
    except Exception as e:
        logger.warning(f"[Reddit] Error fetching posts: {e}")
        return []

async def fetch_twitter_posts(ticker: str) -> List[SocialMediaPost]:
    try:
        headers = {"Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"}
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://api.twitter.com/2/tweets/search/recent?query={ticker}&max_results=10&tweet.fields=created_at"
            response = await client.get(url, headers=headers)
            data = response.json()
            return [
                SocialMediaPost(
                    platform="twitter",
                    content=tweet["text"],
                    timestamp=datetime.strptime(tweet["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                )
                for tweet in data.get("data", [])
            ]
    except Exception as e:
        logger.warning(f"[Twitter] Error fetching posts: {e}")
        return []

async def fetch_news(ticker: str) -> List[str]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = (
                f"https://newsapi.org/v2/everything?q={ticker}"
                f"&from={(datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')}"
                f"&sortBy=publishedAt&apiKey={settings.GOOGLE_NEWS_API_KEY}"
            )
            response = await client.get(url)
            data = response.json()
            return [a["title"] for a in data.get("articles", [])][:10]
    except Exception as e:
        logger.warning(f"[Google News] Error fetching news: {e}")
        return []

async def fetch_historical_prices(ticker: str) -> List[float]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={settings.ALPHA_VANTAGE_API_KEY}"
            response = await client.get(url)
            data = response.json().get("Time Series (Daily)", {})
            return [float(day["4. close"]) for _, day in sorted(data.items())][-30:]
    except Exception as e:
        logger.warning(f"[Alpha Vantage] Fallback to Finnhub due to: {e}")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = (
                f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}"
                f"&resolution=D&from={int((datetime.utcnow() - timedelta(days=30)).timestamp())}"
                f"&to={int(datetime.utcnow().timestamp())}&token={settings.FINNHUB_API_KEY}"
            )
            response = await client.get(url)
            data = response.json()
            return data.get("c", [])
    except Exception as e:
        logger.error(f"[Finnhub] Failed to fetch prices: {e}")
        return []