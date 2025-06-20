import time
from datetime import datetime
from typing import List
import numpy as np
from fastapi import HTTPException
from loguru import logger

from app.models.schemas import StockPredictionRequest, StockPrediction
from app.services import data_sources, ai_reasoning

def linear_regression_prediction(prices: List[float]) -> float:
    if len(prices) < 2:
        raise ValueError("At least two prices are required for regression.")
    x = np.arange(len(prices))
    y = np.array(prices)
    a, b = np.polyfit(x, y, 1)
    next_x = len(prices)
    predicted_price = a * next_x + b
    return round(predicted_price, 2)

def calculate_confidence(sentiment: str, post_count: int) -> float:
    sentiment = sentiment.lower()
    if post_count >= 20 and sentiment in ("positive", "negative"):
        return 0.9
    elif post_count >= 10:
        return 0.75
    else:
        return 0.5

async def generate_prediction(req: StockPredictionRequest) -> StockPrediction:
    start = time.time()

    reddit_posts = await data_sources.fetch_reddit_posts(req.ticker) if req.include_reddit else []
    twitter_posts = await data_sources.fetch_twitter_posts(req.ticker) if req.include_posts else []
    google_news_posts = await data_sources.fetch_news_google(req.ticker)
    prices = await data_sources.fetch_historical_prices(req.ticker)

    logger.info(f"[Reddit] Posts fetched: {len(reddit_posts)}")
    logger.info(f"[Twitter] Posts fetched: {len(twitter_posts)}")
    logger.info(f"[Google News] Posts fetched: {len(google_news_posts)}")
    logger.info(f"[Prices] Data fetched: {prices}")

    all_texts = [p.content for p in reddit_posts + twitter_posts + google_news_posts]
    sentiment_obj = ai_reasoning.analyze_sentiment(all_texts)
    sentiment_label = sentiment_obj.get("sentiment", "neutral").lower()

    direction = "up" if "positive" in sentiment_label else "down"
    post_count = len(reddit_posts + twitter_posts + google_news_posts)
    confidence_score = calculate_confidence(sentiment_label, post_count)

    try:
        latest_price = prices[-1]
        predicted_price = linear_regression_prediction(prices)
        price_diff = predicted_price - latest_price
        price_change_percent = (price_diff / latest_price) * 100
    except Exception as e:
        logger.warning(f"[Price Prediction] Unable to calculate prediction: {e}")
        latest_price = prices[-1] if prices else None
        predicted_price = None
        price_diff = 0
        price_change_percent = 0
        confidence_score = min(confidence_score, 0.2)  # מורידים את הביטחון

    return StockPrediction(
        ticker=req.ticker,
        prediction_time=datetime.utcnow(),
        timeframe=req.timeframe,
        prediction={
            "direction": direction,
            "sentiment": sentiment_label,
            "confidence": confidence_score,
            "price_target": round(predicted_price, 2) if predicted_price is not None else None,
            "reasoning": sentiment_obj.get("reasoning", "")
        },
        technical_signals={
            "trend": direction,
            "latest_price": latest_price,
            "price_change": round(price_diff, 2),
            "price_change_percent": round(price_change_percent, 2)
        },
        sentiment_analysis=sentiment_obj,
        confidence=confidence_score,
        supporting_data={
            "post_count": post_count,
            "influencer_post_count": len(twitter_posts)
        },
        posts=reddit_posts + twitter_posts + google_news_posts,
        processing_time=round(time.time() - start, 2)
    )