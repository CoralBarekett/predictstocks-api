from typing import List, Dict, Any
from openai import OpenAI
from loguru import logger
from app.core.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_sentiment(posts: List[str]) -> Dict[str, Any]:
    if not posts:
        logger.warning("[Sentiment] No posts provided — returning neutral fallback")
        return {
            "sentiment": "neutral",
            "impact": "low",
            "confidence": "low",
            "key_factors": [],
            "patterns": [],
            "reasoning": "Not enough posts provided for meaningful analysis."
        }

    try:
        prompt = f"""
You are a financial sentiment analysis assistant.

Given the following social media posts and news headlines about a stock, analyze and return:
- overall sentiment: positive / neutral / negative
- impact level: high / medium / low
- confidence level: high / medium / low
- list of key factors mentioned
- patterns or signals observed
- a short reasoning explaining your conclusion

Posts:
{chr(10).join(posts[:10])}

Respond only in the following JSON format:
{{
  "sentiment": "...",
  "impact": "...",
  "confidence": "...",
  "key_factors": ["...", "..."],
  "patterns": ["...", "..."],
  "reasoning": "..."
}}
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes stock-related sentiment."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.5,
            max_tokens=500
        )

        raw = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw)
            logger.info("[Sentiment] AI structured sentiment analysis completed.")
            return parsed
        except json.JSONDecodeError:
            logger.warning("[Sentiment] Failed to parse GPT response as JSON, returning fallback reasoning.")
            return {
                "sentiment": "neutral",
                "impact": "low",
                "confidence": "low",
                "key_factors": [],
                "patterns": [],
                "reasoning": raw   
            }

    except Exception as e:
        logger.error(f"[OpenAI] Sentiment analysis failed: {e}")
        return {
            "sentiment": "neutral",
            "impact": "low",
            "confidence": "low",
            "key_factors": [],
            "patterns": [],
            "reasoning": "An error occurred while analyzing sentiment. Default values returned."
        }