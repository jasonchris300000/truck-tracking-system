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
        function sendLocation(pos) {
            var lat = pos.coords.latitude;
            var lng = pos.coords.longitude;
            var speed = pos.coords.speed ? (pos.coords.speed * 3.6).toFixed(1) : 0;
            document.getElementById('coords').innerText = 'Lat: ' + lat.toFixed(4) + ' Lng: ' + lng.toFixed(4);
            fetch('/update-location', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ truck_id: driverName, latitude: lat, longitude: lng, speed: speed })
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
    now = time.time()
    clean_trucks = {
        tid: {"latitude": data["latitude"], "longitude": data["longitude"], "speed": data["speed"]}
        for tid, data in truck_locations.items()
    }
    trucks_json = json.dumps(clean_trucks)
    inactive = [tid for tid, data in truck_locations.items() if now - data.get("last_seen", now) > 60]
    inactive_json = json.dumps(inactive)
    sidebar_cards = "".join([
        f'<div class="truck-card"><div class="truck-name">{tid}</div><div class="truck-speed">Speed: {data["speed"]} km/h</div></div>'
        for tid, data in truck_locations.items()
    ])

    return """<!DOCTYPE html>
<html>
<head>
    <title>Truck Tracker</title>
    <meta http-equiv="refresh" content="5">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial; background: #1a1a2e; color: white; height: 100vh; display: flex; flex-direction: column; }
        #header { padding: 15px; background: #16213e; text-align: center; font-size: 22px; flex-shrink: 0; }
        #main { display: flex; flex: 1; overflow: hidden; }
        #map { flex: 1; }
        #sidebar { width: 240px; background: #16213e; overflow-y: auto; padding: 10px; flex-shrink: 0; }
        #sidebar h3 { text-align: center; border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 10px; }
        .truck-card { background: #0f3460; border-radius: 8px; padding: 10px; margin-bottom: 10px; }
        .truck-name { font-size: 16px; font-weight: bold; color: #e74c3c; }
        .truck-speed { font-size: 13px; color: #aaa; margin-top: 4px; }
        #info { padding: 10px; background: #16213e; text-align: center; flex-shrink: 0; }
    </style>
</head>
<body>
    <div id="header">LIVE TRUCK TRACKER - KAMPALA</div>
    <div id="main">
        <div id="map"></div>
        <div id="sidebar">
            <h3>Active Trucks</h3>
            """ + sidebar_cards + """
        </div>
    </div>
    <div id="info">Auto-refreshes every 5 seconds</div>
    <script>
        var savedLat = localStorage.getItem('mapLat') || 0.3476;
        var savedLng = localStorage.getItem('mapLng') || 32.5825;
        var savedZoom = localStorage.getItem('mapZoom') || 13;
        var map = L.map('map').setView([savedLat, savedLng], savedZoom);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        map.on('moveend', function() {
            localStorage.setItem('mapLat', map.getCenter().lat);
            localStorage.setItem('mapLng', map.getCenter().lng);
            localStorage.setItem('mapZoom', map.getZoom());
        });
        var trucks = """ + trucks_json + """;
        for (var id in trucks) {
            var t = trucks[id];
            L.circleMarker([t.latitude, t.longitude], {
                radius: 12, color: 'red', fillColor: 'red', fillOpacity: 1
            }).addTo(map).bindPopup(id + '<br>Speed: ' + t.speed + ' km/h');
        }
        var inactive = """ + inactive_json + """;
        inactive.forEach(function(tid) {
            if (!document.getElementById('warning-' + tid)) {
                var div = document.createElement('div');
                div.id = 'warning-' + tid;
                div.style.cssText = 'background:#e74c3c; padding:10px; margin:10px; border-radius:8px; text-align:center; position:fixed; top:70px; left:50%; transform:translateX(-50%); z-index:9999; min-width:300px;';
                div.innerHTML = '<b>' + tid + '</b> has gone offline!<br><br>' +
                    '<button onclick="markDone(\'' + tid + '\')" style="background:white; color:red; border:none; padding:5px 10px; border-radius:5px; cursor:pointer; margin-right:5px">Mark as Done</button>' +
                    '<button onclick="keepTracking(\'' + tid + '\')" style="background:#2ecc71; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;">Keep Tracking</button>';
                document.body.appendChild(div);
            }
        });
        function markDone(tid) {
            fetch('/remove-truck/' + tid, {method: 'DELETE'});
            document.getElementById('warning-' + tid).remove();
        }
        function keepTracking(tid) {
            document.getElementById('warning-' + tid).remove();
        }
    </script>
</body>
</html>"""