import httpx

async def test_yahoo_api():
    url = "https://yahoo-finance15.p.rapidapi.com/api/v1/markets/news"
    headers = {
        "x-rapidapi-key": "02d0bc720fmsh7586e8f9fa14a64p1d24adjsn0c9da2ef91dc",
        "x-rapidapi-host": "yahoo-finance15.p.rapidapi.com"
    }
    params = {
        "tickers": "AAPL"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=headers, params=params)
        print(response.status_code)
        print(response.text)

import asyncio
asyncio.run(test_yahoo_api())