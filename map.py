import folium
import requests

response = requests.get("http://127.0.0.1:8000/trucks")
trucks = response.json()

m = folium.Map(location=[0.3476, 32.5825], zoom_start=14)

for truck_id, data in trucks.items():
    folium.CircleMarker(
        location=[data["latitude"], data["longitude"]],
        radius=6,
        color="black",
        fill=True,
        fill_color="black",
        fill_opacity=1.0,
        popup=f"{truck_id} | Speed: {data['speed']} km/h"
    ).add_to(m)

m.save("map.html")
print("Map saved! Open map.html in your browser.")