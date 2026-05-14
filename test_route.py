import requests
import json

data = {
    "day": 1,
    "group_id": 1,
    "stops": [5, 23, 87, 145, 678],
    "total_time": 420
}

response = requests.post("http://127.0.0.1:5000/route", json=data)
print(response.status_code)
print(response.json())
