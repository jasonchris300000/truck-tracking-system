import requests
import time
import random

# Starting position - Mulago, Kampala
lat = 0.3476
lng = 32.5825

print("Simulator running... watch your dashboard!")

while True:
    # Move the truck slightly each time
    lat += random.uniform(-0.001, 0.001)
    lng += random.uniform(-0.001, 0.001)
    speed = random.uniform(20, 80)

    requests.post(
        "http://127.0.0.1:8001/update-location",
        json={
            "truck_id": "TRUCK_1",
            "latitude": lat,
            "longitude": lng,
            "speed": round(speed, 1)
        }
    )

    print(f"Sent: lat={lat:.4f}, lng={lng:.4f}, speed={speed:.1f}")
    time.sleep(3)