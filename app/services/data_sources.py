import time
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from app.models.schemas import SocialMediaPost
from app.core.config import settings
from newspaper import Article

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
            posts = [
                SocialMediaPost(
                    platform="reddit",
                    content=post["data"]["title"],
                    timestamp=datetime.utcfromtimestamp(post["data"]["created_utc"])
                )
                for post in data["data"]["children"]
            ][:10]
            if not posts:
                logger.warning(f"[Reddit] No posts found for {ticker}")
            return posts
    except Exception as e:
        logger.warning(f"[Reddit] Error fetching posts: {e}")
        return []
    

async def fetch_twitter_posts(ticker: str, max_results: int = 30) -> List[SocialMediaPost]:
    logger.info(f"[Twitter/API] Fetching tweets for: {ticker}")
    tweets: List[SocialMediaPost] = []

    try:
        bearer_token = settings.TWITTER_BEARER_TOKEN
        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }

        query = f"{ticker} lang:en -is:retweet"
        url = (
            f"https://api.twitter.com/2/tweets/search/recent?"
            f"query={query}&max_results={min(max_results, 100)}&tweet.fields=created_at,author_id,text"
        )

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"[Twitter/API] Failed to fetch tweets: {response.status_code} {response.text}")
                return []
            data = response.json().get("data", [])

            for tweet in data:
                tweets.append(SocialMediaPost(
                    platform="twitter",
                    content=tweet["text"],
                    timestamp=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                    url=f"https://twitter.com/i/web/status/{tweet['id']}",
                    username=tweet.get("author_id")
                ))

        logger.info(f"[Twitter/API] Fetched {len(tweets)} tweets")
        return tweets

    except Exception as e:
        logger.warning(f"[Twitter/API] Error fetching tweets: {e}")
        return []


async def fetch_news_google(ticker: str) -> List[SocialMediaPost]:
    try:
        cx = settings.GOOGLE_SEARCH_ENGINE_ID 
        api_key = settings.GOOGLE_NEWS_API_KEY 
        query = f"{ticker} stock news"

        url = (
            f"https://www.googleapis.com/customsearch/v1?"
            f"q={query}&cx={cx}&key={api_key}"
        )

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            data = response.json()
            logger.info(f"[Google Custom Search] Fetched {len(data.get('items', []))} items for query: {query}")

            posts = []
            for item in data.get("items", [])[:10]:
                article_url = item.get("link")
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                timestamp = datetime.utcnow()

                text_content = ""

                # Skip known blocked domains
                if "investors.com" in article_url:
                    logger.warning(f"[Scraper] Skipping blocked domain: {article_url}")
                else:
                    try:
                        article = Article(article_url)
                        article.download()
                        article.parse()
                        text_content = article.text.strip()

                        if text_content:
                            logger.info(f"[Scraper] Successfully parsed article: {article_url}")
                    except Exception as e:
                        logger.warning(f"[Scraper] Failed to parse article at {article_url}: {e}")

                # Use full article content if available, otherwise fallback to title/snippet
                final_content = text_content or title or snippet

                if final_content:
                    posts.append(SocialMediaPost(
                        platform="google_news",
                        content=final_content,
                        timestamp=timestamp,
                        url=article_url
                    ))
                else:
                    logger.warning(f"[Scraper] No usable content from: {article_url}")

            if not posts:
                logger.warning(f"[Google News] No articles parsed successfully for {ticker}")
            return posts
    except Exception as e:
        logger.warning(f"[Google Custom Search] Error fetching news: {e}")
        return []


def scrape_article_text(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logger.warning(f"[Scraper] Failed to parse article at {url}: {e}")
        return ""

async def fetch_historical_prices(ticker: str) -> List[float]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={settings.ALPHA_VANTAGE_API_KEY}"
            response = await client.get(url)
            data = response.json().get("Time Series (Daily)", {})
            prices = [float(day["4. close"]) for _, day in sorted(data.items())][-30:]
            if not prices:
                logger.warning(f"[Alpha Vantage] No prices returned for {ticker}")
            return prices
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
            prices = data.get("c", [])
            if not prices:
                logger.warning(f"[Finnhub] No closing prices returned for {ticker}")
            return prices
    except Exception as e:
        logger.error(f"[Finnhub] Failed to fetch prices: {e}")
        return []