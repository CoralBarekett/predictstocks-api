import time
from datetime import datetime
from app.models.schemas import StockPredictionRequest, StockPrediction
from app.services import data_sources, ai_reasoning

async def generate_prediction(req: StockPredictionRequest) -> StockPrediction:
    start = time.time()

    reddit_posts = await data_sources.fetch_reddit_posts(req.ticker) if req.include_reddit else []
    twitter_posts = await data_sources.fetch_twitter_posts(req.ticker) if req.include_posts else []
    google_news_posts = await data_sources.fetch_news_google(req.ticker)
    prices = await data_sources.fetch_historical_prices(req.ticker)

    all_texts = [p.content for p in reddit_posts + twitter_posts + google_news_posts]
    sentiment = ai_reasoning.analyze_sentiment(all_texts)

    direction = "up" if "positive" in sentiment.lower() else "down"
    latest_price = prices[-1] if prices else 100.0
    predicted_price = latest_price * (1.02 if direction == "up" else 0.98)

    return StockPrediction(
        ticker=req.ticker,
        prediction_time=datetime.utcnow(),
        timeframe=req.timeframe,
        prediction={
            "direction": direction,
            "sentiment": sentiment,
            "confidence": 0.75,
            "price_target": round(predicted_price, 2),
            "reasoning": sentiment
        },
        technical_signals={
            "trend": direction,
            "latest_price": latest_price,
            "price_change": round(predicted_price - latest_price, 2),
            "price_change_percent": round(((predicted_price - latest_price) / latest_price) * 100, 2)
        },
        sentiment_analysis=sentiment,
        confidence=0.75,
        supporting_data={
            "post_count": len(reddit_posts + twitter_posts + google_news_posts),
            "influencer_post_count": len(twitter_posts)
        },
        posts=reddit_posts + twitter_posts + google_news_posts,
        processing_time=round(time.time() - start, 2)
    )

from fastapi import APIRouter
from app.models.schemas import StockPredictionRequest, StockPrediction
from app.services.predictor import generate_prediction

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/predict", response_model=StockPrediction)
async def predict_stock(req: StockPredictionRequest):
    return await generate_prediction(req)