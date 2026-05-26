from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import time

app = FastAPI()

truck_locations = {}

class LocationUpdate(BaseModel):
    truck_id: str
    latitude: float
    longitude: float
    speed: float = 0.0

@app.post("/update-location")
def update_location(location: LocationUpdate):
    truck_locations[location.truck_id] = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "speed": location.speed,
        "last_seen": time.time()
    }
    return {"status": "ok", "truck_id": location.truck_id}

@app.get("/trucks")
def get_trucks():
    return truck_locations

@app.delete("/remove-truck/{truck_id}")
def remove_truck(truck_id: str):
    if truck_id in truck_locations:
        del truck_locations[truck_id]
    return {"status": "removed", "truck_id": truck_id}

@app.get("/driver", response_class=HTMLResponse)
def driver():
    return """<!DOCTYPE html>
<html>
<head><title>Driver Tracker</title></head>
<body style="font-family:Arial; text-align:center; padding:40px; background:#1a1a2e; color:white;">
    <h2>Driver Tracker</h2>
    <div id="login">
        <p>Enter your name to start tracking:</p>
        <input id="nameInput" type="text" placeholder="Your name" 
            style="padding:10px; font-size:16px; border-radius:8px; border:none; margin-bottom:15px;">
        <br>
        <button onclick="startTracking()" 
            style="padding:10px 30px; font-size:16px; background:#e74c3c; color:white; border:none; border-radius:8px; cursor:pointer;">
            Start Tracking
        </button>
    </div>
    <div id="tracking" style="display:none;">
        <p id="status">Sending location...</p>
        <p id="coords"></p>
    </div>
    <script>
        var driverName = "";
        function startTracking() {
            driverName = document.getElementById('nameInput').value.trim();
            if (!driverName) { alert("Please enter your name"); return; }
            document.getElementById('login').style.display = 'none';
            document.getElementById('tracking').style.display = 'block';
            setInterval(function() {
                navigator.geolocation.getCurrentPosition(sendLocation, error);
            }, 3000);
        }
        function