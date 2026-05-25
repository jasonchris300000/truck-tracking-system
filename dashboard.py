from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json

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
        "speed": location.speed
    }
    return {"status": "ok", "truck_id": location.truck_id}

@app.get("/trucks")
def get_trucks():
    return truck_locations


@app.get("/driver", response_class=HTMLResponse)
def driver():
    return """<!DOCTYPE html>
<html>
<head><title>Driver Tracker</title></head>
<body style="font-family:Arial; text-align:center; padding:40px; background:#1a1a2e; color:white;">
    <h2>Driver Tracker</h2>
    <div id="login" >
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
            if (!driverName) {
                alert("Please enter your name");
                return;
            }
            document.getElementById('login').style.display = 'none';
            document.getElementById('tracking').style.display = 'block';
            setInterval(function() {
                navigator.geolocation.getCurrentPosition(sendLocation, error);
            }, 3000);

        }
        function sendLocation(pos) {
            var lat = pos.coords.latitude;
            var lng = pos.coords.longitude;
            var speed = pos.coords.speed || 0;
            document.getElementById('coords').innerText = 'Lat: ' + lat.toFixed(4) + ' Lng: ' + lng.toFixed(4);
            fetch('/update-location', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    truck_id: driverName,
                    latitude: lat,
                    longitude: lng,
                    speed: speed
                })
            });
            document.getElementById('status').innerText = 'Sending location as: ' + driverName;
        }
        function error() {
            document.getElementById('status').innerText = 'GPS error - allow location access';
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def dashboard():
    trucks_json = json.dumps(truck_locations)
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Truck Tracker</title>
    <meta http-equiv="refresh" content="5">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <style>
        body { margin: 0; font-family: Arial; background: #1a1a2e; color: white; }
        #header { padding: 15px; background: #16213e; text-align: center; font-size: 22px; }
        #map { height: 80vh; width: 100%; }
        #info { padding: 10px; background: #16213e; text-align: center; }
    </style>
</head>
<body>
    <div id="header">LIVE TRUCK TRACKER - KAMPALA</div>
    <div id="map"></div>
    <div id="info">Auto-refreshes every 5 seconds</div>
    <script>
        var map = L.map('map').setView([0.3476, 32.5825], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        var trucks = """ + trucks_json + """;
        for (var id in trucks) {
            var t = trucks[id];
            L.circleMarker([t.latitude, t.longitude], {
                radius: 12,
                color: 'red',
                fillColor: 'red',
                fillOpacity: 1
            }).addTo(map).bindPopup(id + '<br>Speed: ' + t.speed + ' km/h');
        }
    </script>
</body>
</html>"""
    return html
