from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

truck_locations = {}

class LocationUpdate(BaseModel):
    truck_id: str
    latitude: float
    longitude: float
    speed: float = 0.0

@app.post("/update-location")
def update_location(data: LocationUpdate):
    truck_locations[data.truck_id] = {
        "latitude": data.latitude,
        "longitude": data.longitude,
        "speed": data.speed
    }
    return {"status": "ok", "truck_id": data.truck_id}

@app.get("/trucks")
def get_trucks():
    return truck_locations