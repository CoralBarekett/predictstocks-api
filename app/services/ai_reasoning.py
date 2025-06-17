from openai import OpenAI
from typing import List
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_sentiment(posts: List[str]) -> str:
    prompt = f"Analyze the sentiment of the following posts: {posts}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content