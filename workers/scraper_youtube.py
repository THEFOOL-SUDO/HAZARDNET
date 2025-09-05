# workers/scraper_youtube.py
from youtubesearchpython import VideosSearch
import requests, time

API = "http://localhost:8000/signals"
QUERIES = ["flood chennai news", "oil spill goa", "capsize mangalore"]

def fetch(query, limit=3):
    vs = VideosSearch(query, limit=limit)
    res = vs.result().get("result", [])
    for it in res:
        title = it.get("title")
        link = it.get("link")
        snippet = it.get("descriptionSnippet") or []
        text = title + " " + " ".join([s.get("text","") for s in snippet])
        payload = {"text": text, "source":"youtube", "media_url": link}
        try:
            requests.post(API, json=payload, timeout=8)
        except Exception as e:
            print("post err", e)

if __name__ == "__main__":
    while True:
        for q in QUERIES:
            fetch(q, limit=2)
            time.sleep(1)
        time.sleep(60)
