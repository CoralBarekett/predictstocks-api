import requests
import json

def test_reddit():
    print("\n=== Testing Reddit API ===")
    auth = requests.auth.HTTPBasicAuth("m4ZO8icQDjjUjjcMezU9nw", "rW8ohsa5frCISPbFhIaCmDu2r3gbEg")
    headers = {"User-Agent": "test-script"}
    data = {
        "grant_type": "password",
        "username": "OddChildhood3903",
        "password": "reddit123coral"
    }

    try:
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Reddit authentication successful!")
            print("Access Token:", token[:10] + "...")
        else:
            print("❌ Reddit auth failed:", response.text)
            if response.headers.get("Content-Type", "").startswith("application/json"):
                print("Response JSON:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"❌ Exception during Reddit auth: {e}")


def test_twitter():
    print("\n=== Testing Twitter API ===")
    bearer_token = "Bearer AAAAAAAAAAAAAAAAAAAAADbu0wEAAAAALmTya3BgF7sdhhH9AplTpQy0WO0%3DLQXH75P5qEf9ex5FGXz8xADqA7dodryNYIsCB2pBxEXXaC3kRE"
    headers = {
        "Authorization": bearer_token
    }

    url = "https://api.twitter.com/2/tweets/search/recent?query=AAPL&max_results=1&tweet.fields=created_at"

    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Twitter API working — Tweet found:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ Twitter API error:", response.status_code)
            if response.headers.get("Content-Type", "").startswith("application/json"):
                print("Response JSON:", json.dumps(response.json(), indent=2))
            else:
                print("Response Text:", response.text)
    except Exception as e:
        print(f"❌ Exception during Twitter test: {e}")


def test_google_news():
    print("\n=== Testing Google News API ===")
    url = (
        "https://www.googleapis.com/customsearch/v1"
        "?q=AAPL+stock+news"
        "&cx=b5ebd157c1cbb4d7f"
        "&key=AIzaSyAUgGLCVCO9nl_rVdt0o_kAifXMxctfe2k"
    )

    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            items = response.json().get("items", [])
            print(f"✅ Google News returned {len(items)} results")
            for i, item in enumerate(items[:3]):
                print(f"- {item.get('title')} ({item.get('link')})")
        else:
            print("❌ Google API error:", response.status_code)
            if response.headers.get("Content-Type", "").startswith("application/json"):
                print("Response JSON:", json.dumps(response.json(), indent=2))
            else:
                print("Response Text:", response.text)
    except Exception as e:
        print(f"❌ Exception during Google News test: {e}")


if __name__ == "__main__":
    test_reddit()
    test_twitter()
    test_google_news()