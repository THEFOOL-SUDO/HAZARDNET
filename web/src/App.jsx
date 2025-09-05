import React from "react";
import MapView from "./components/MapView";
import ExampleHazard from "./components/ExampleHazard";

function App(){
  return (
    <div style={{padding:20}}>
      <h1>HazardNet — Live Scraping & Clustering Demo</h1>
      <div style={{display:"flex",gap:20}}>
        <div style={{flex:1}}>
          <MapView />
        </div>
        <div style={{width:320}}>
          <h3>Examples (hover)</h3>
          <ExampleHazard keyword="Flood" region="Chennai" />
          <div style={{height:12}} />
          <ExampleHazard keyword="Oil spill" region="Goa" />
        </div>
      </div>
    </div>
  );
}

export default App;
