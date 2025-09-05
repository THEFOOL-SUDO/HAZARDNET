// web/src/components/MapView.jsx
import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import L from "leaflet";

export default function MapView() {
  const [incidents, setIncidents] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    // Load initial incidents
    fetch("http://localhost:8000/incidents").then(r => r.json()).then(setIncidents).catch(console.error);

    // Connect WS
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onopen = () => console.log("ws open");
    ws.onmessage = (evt) => {
      const msg = JSON.parse(evt.data);
      // message types: signal -> contains cluster_id; we will reload incidents summary
      if (msg.type === "signal") {
        // naive: re-fetch incidents summary (simpler than sending full cluster data)
        fetch("http://localhost:8000/incidents").then(r=>r.json()).then(setIncidents).catch(console.error);
      }
    };
    ws.onclose = () => console.log("ws closed");
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  return (
    <MapContainer center={[15.3, 73.9]} zoom={6} style={{ height: "70vh" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {incidents.map(it => it.lat && it.lon ? (
        <Marker key={it.cluster_id} position={[it.lat, it.lon]}>
          <Popup>
            <strong>{it.title}</strong><br/>
            Confidence: {Math.round((it.confidence||0)*100)}%<br/>
            Last: {it.last_seen}
          </Popup>
        </Marker>
      ) : null)}
    </MapContainer>
  );
}
