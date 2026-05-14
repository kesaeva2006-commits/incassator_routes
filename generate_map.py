import folium
import requests

url = 'https://raw.githubusercontent.com/kesaeva2006-commits/incassator_routes/feature/backend/atms.json'
response = requests.get(url)
atms = response.json()

m = folium.Map(location=[55.75, 37.62], zoom_start=11)

for atm in atms:
    folium.CircleMarker(
        location=[atm['lat'], atm['lon']],
        radius=3,
        color='#279ed1',
        fill=True,
        fill_color='#279ed1',
        popup=f"ID: {atm['id']}"
    ).add_to(m)

m.save('map.html')
print("Карта с банкоматами готова")