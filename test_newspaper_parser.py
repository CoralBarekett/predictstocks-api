import requests
from newspaper import Article

url = "https://www.investors.com/news/technology/aapl-stock-apple-earnings-fiscal-third-quarter-2022/"
print("=== Testing article parsing ===")
print(f"URL: {url}")

try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch page. Status: {response.status_code}")
    else:
        article = Article(url)
        article.download(input_html=response.text)
        print("✅ Downloaded manually")

        article.parse()
        print("✅ Parsed successfully")
        print("Title:", article.title)
        print("Text Preview:", article.text[:500])
except Exception as e:
    print("❌ Failed to parse article:", e)