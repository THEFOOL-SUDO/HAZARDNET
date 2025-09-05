# app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, json, datetime, sqlite3, numpy as np, pickle, base64

from .db import DB_CONN
from .clusterer import add_signal_embedding, run_clustering, labels_for_signal

app = FastAPI(title="HazardNet Real-time")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Simple WebSocket manager to broadcast to all connected clients
class ConnectionManager:
    def __init__(self):
        self.active = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: dict):
        text = json.dumps(message)
        to_remove = []
        for ws in list(self.active):
            try:
                await ws.send_text(text)
            except:
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(ws)

manager = ConnectionManager()

# Pydantic model for incoming signals (from scrapers)
class SignalIn(BaseModel):
    source: str = "scraper"
    text: str
    lat: float | None = None
    lon: float | None = None
    media_url: str | None = None

@app.post("/signals")
async def ingest_signal(sig: SignalIn, bg: BackgroundTasks):
    sid = str(uuid.uuid4())
    ts = datetime.datetime.utcnow().isoformat()
    # Persist text & metadata to sqlite
    cur = DB_CONN.cursor()
    cur.execute("INSERT INTO signals (id, source, text, lat, lon, media_url, cluster_id, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (sid, sig.source, sig.text, sig.lat, sig.lon, sig.media_url, -1, ts))
    DB_CONN.commit()
    # Add embedding and trigger clustering in background
    bg.add_task(process_and_cluster, sid, sig.text, sig.lat, sig.lon, sig.media_url, ts)
    return {"signal_id": sid, "status": "queued"}

def process_and_cluster(sid, text, lat, lon, media_url, ts):
    # 1. create embedding and add to memory
    emb = add_signal_embedding(sid, text)
    # 2. run clustering over whole set (small-scale)
    labels = run_clustering(min_cluster_size=2)
    # 3. store cluster id for this signal in DB
    idx = None
    from .clusterer import SIGNAL_IDS
    if sid in SIGNAL_IDS:
        idx = SIGNAL_IDS.index(sid)
    cluster_id = labels[idx] if idx is not None else -1
    cur = DB_CONN.cursor()
    cur.execute("UPDATE signals SET cluster_id = ? WHERE id = ?", (int(cluster_id), sid))
    DB_CONN.commit()
    # 4. compute cluster centroid & upsert into incidents table
    update_incident_from_cluster(cluster_id)
    # 5. broadcast update (very small message)
    import asyncio
    payload = {"type":"signal", "id":sid, "text":text, "lat":lat, "lon":lon, "cluster_id":int(cluster_id), "ts":ts}
    try:
        asyncio.run(manager.broadcast(payload))
    except Exception as e:
        # in uvicorn background thread this may fail; ignore for demo
        print("broadcast err", e)

def update_incident_from_cluster(cluster_id):
    # gather signals in this cluster, compute centroid and upsert incident row
    cur = DB_CONN.cursor()
    cur.execute("SELECT id, lat, lon FROM signals WHERE cluster_id = ?", (int(cluster_id),))
    rows = cur.fetchall()
    if not rows:
        return
    # compute centroid from available lat/lon (ignore None)
    lats = [r[1] for r in rows if r[1] is not None]
    lons = [r[2] for r in rows if r[2] is not None]
    if lats and lons:
        centroid_lat = sum(lats)/len(lats)
        centroid_lon = sum(lons)/len(lons)
    else:
        centroid_lat = None; centroid_lon = None
    now = datetime.datetime.utcnow().isoformat()
    # upsert incident
    cur.execute("SELECT id FROM incidents WHERE cluster_id = ?", (int(cluster_id),))
    r = cur.fetchone()
    if r:
        cur.execute("UPDATE incidents SET centroid_lat=?, centroid_lon=?, last_seen=? WHERE cluster_id=?",
                    (centroid_lat, centroid_lon, now, int(cluster_id)))
    else:
        title = f"Incident {cluster_id}"
        cur.execute("INSERT INTO incidents (cluster_id, title, centroid_lat, centroid_lon, confidence, last_seen) VALUES (?,?,?,?,?,?)",
                    (int(cluster_id), title, centroid_lat, centroid_lon, 0.5, now))
    DB_CONN.commit()

@app.get("/incidents")
async def list_incidents():
    cur = DB_CONN.cursor()
    cur.execute("SELECT cluster_id, title, centroid_lat, centroid_lon, confidence, last_seen FROM incidents")
    rows = cur.fetchall()
    out = []
    for r in rows:
        out.append({"cluster_id": r[0], "title": r[1], "lat": r[2], "lon": r[3], "confidence": r[4], "last_seen": r[5]})
    return out

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keep connection alive; client can send pings
    except WebSocketDisconnect:
        manager.disconnect(ws)
print('Hello from backend')
