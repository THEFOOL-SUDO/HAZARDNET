
# workers/scraper_x.py
import snscrape.modules.twitter as sntwitter
import time, requests

API = "http://api:8000/signals"  # when using docker compose; for local use use http://localhost:8000/signals
# Keywords to track in real time (customize)
KEYWORDS = ["flood", "oil spill", "capsize", "cyclone", "distress"]

def post_signal(text, lat=None, lon=None):
    payload = {"text": text, "source": "x", "lat": lat, "lon": lon}
    try:
        requests.post(API, json=payload, timeout=8)
    except Exception as e:
        print("post err", e)

def fetch_keyword(k, limit=10):
    query = f"{k} lang:en"
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= limit: break
        txt = tweet.content
        post_signal(txt)

if __name__ == "__main__":
    while True:
        for k in KEYWORDS:
            print("fetching", k)
            try:
                fetch_keyword(k, limit=5)
            except Exception as e:
                print("err", e)
            time.sleep(1)
        time.sleep(20)
