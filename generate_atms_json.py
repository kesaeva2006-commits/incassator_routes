import json
from generator import generate_atms

def save_atms_to_json(filename='atms.json'):
    atms = generate_atms(1000, seed=42)
    data = []
    for a in atms:
        data.append({
            'id': a.id,
            'lat': a.lat,
            'lon': a.lon,
            'capacity_in': a.capacity_in,
            'capacity_out': a.capacity_out,
            'mean_in': a.mean_in,
            'std_in': a.std_in,
            'mean_out': a.mean_out,
            'std_out': a.std_out
        })
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    save_atms_to_json()
