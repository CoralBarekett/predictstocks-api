from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class StockPredictionRequest(BaseModel):
    ticker: str
    timeframe: str = Field(default="1d", pattern=r"^(1d|1w|1m)$")
    include_posts: bool = False
    include_reddit: bool = True


class SocialMediaPost(BaseModel):
    platform: str
    content: str
    timestamp: datetime
    url: Optional[str] = None
    username: Optional[str] = None


class SentimentAnalysis(BaseModel):
    sentiment: str
    impact: str
    confidence: str
    key_factors: List[str] = []
    patterns: List[str] = []
    reasoning: str


class StockPrediction(BaseModel):
    ticker: str
    prediction_time: datetime
    timeframe: str
    prediction: Dict[str, Any]
    technical_signals: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[SentimentAnalysis] = None
    confidence: Optional[float] = None
    supporting_data: Dict[str, Any] = {}
    posts: Optional[List[SocialMediaPost]] = None
    processing_time: float