import requests

def test_reddit():
    print("=== Testing Reddit API ===")
    auth = requests.auth.HTTPBasicAuth("m4ZO8icQDjjUjjcMezU9nw", "rW8ohsa5frCISPbFhIaCmDu2r3gbEg")
    headers = {"User-Agent": "test-script"}
    data = {
        "grant_type": "password",
        "username": "OddChildhood3903",
        "password": "reddit123coral"
    }
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
    if response.status_code == 200:
        print("✅ Reddit authentication successful!")
    else:
        print("❌ Reddit auth failed:", response.status_code, response.text)

def test_twitter():
    print("\n=== Testing Twitter API ===")
    headers = {
        "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAADbu0wEAAAAALmTya3BgF7sdhhH9AplTpQy0WO0%3DLQXH75P5qEf9ex5FGXz8xADqA7dodryNYIsCB2pBxEXXaC3kRE"
    }
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/recent?query=AAPL&max_results=1&tweet.fields=created_at",
        headers=headers
    )
    if response.status_code == 200:
        print("✅ Twitter authentication successful!")
    else:
        print("❌ Twitter auth failed:", response.status_code, response.text)

def test_google_news():
    print("\n=== Testing Google News API ===")
    url = (
        f"https://www.googleapis.com/customsearch/v1?q=AAPL+stock+news&cx=b5ebd157c1cbb4d7f&key=AIzaSyAUgGLCVCO9nl_rVdt0o_kAifXMxctfe2k"
    )
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ Google News API key works!")
    else:
        print("❌ Google News failed:", response.status_code, response.text)

if __name__ == "__main__":
    test_reddit()
    test_twitter()
    test_google_news()