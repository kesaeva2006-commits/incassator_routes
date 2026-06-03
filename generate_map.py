import folium
import json
import os
import random
import math
from atm import Atm   # ← импортируем класс банкомата

#  Генерация карт Москвы: банкоматы цветом по риску + 5 маршрутов
#  Для каждого дня создаётся отдельный файл: map_day1.html, map_day2.html, map_day3.html
#  Frontend — отображение рисков (зелёный/жёлтый/красный) + легенда + кнопки дней

# --- 1. Загрузка банкоматов и создание объектов Atm ---
ATMS_URL = 'https://raw.githubusercontent.com/kesaeva2006-commits/incassator_routes/feature/backend/atms.json'

if os.path.exists('atms.json'):
    with open('atms.json', encoding='utf-8') as f:
        atms_data = json.load(f)
else:
    import requests
    atms_data = requests.get(ATMS_URL).json()

# Превращаем словари в объекты Atm
atms = []
for item in atms_data:
    atm = Atm(
        atm_id=item['id'],
        lat=item['lat'],
        lon=item['lon'],
        capacity_in=item['capacity_in'],
        capacity_out=item['capacity_out'],
        mean_in=item.get('mean_in', 0.0),
        std_in=item.get('std_in', 0.0),
        mean_out=item.get('mean_out', 0.0),
        std_out=item.get('std_out', 0.0)
    )
    # Инициализируем текущие уровни (в atms.json их нет, ставим начало дня)
    atm.current_in = 0
    atm.current_out = atm.capacity_out
    atms.append(atm)

# --- Цвета для маршрутов (5 машин) ---
route_colors = ['red', 'blue', 'green', 'orange', 'purple']
route_names = ['Машина 1', 'Машина 2', 'Машина 3', 'Машина 4', 'Машина 5']

# --- Цвета для риска банкоматов ---
risk_colors = {
    'GREEN': '#2ecc71',   # ярко-зелёный
    'YELLOW': '#f1c40f',  # жёлтый
    'RED': '#e74c3c'      # красный
}

DAYS = 3


def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def kmeans_5(points, k=5, iterations=20):
    """Демо-кластеризация (если нет routes.json)."""
    random.seed(42)
    centers = random.sample(points, k)
    for _ in range(iterations):
        clusters = [[] for _ in range(k)]
        for p in points:
            nearest = min(range(k), key=lambda c: distance(p, centers[c]))
            clusters[nearest].append(p)
        new_centers = []
        for c in range(k):
            if clusters[c]:
                lat = sum(p[0] for p in clusters[c]) / len(clusters[c])
                lon = sum(p[1] for p in clusters[c]) / len(clusters[c])
                new_centers.append([lat, lon])
            else:
                new_centers.append(centers[c])
        if new_centers == centers:
            break
        centers = new_centers
    return clusters


def nearest_neighbor_order(points):
    if not points:
        return []
    remaining = points[:]
    route = [remaining.pop(0)]
    while remaining:
        last = route[-1]
        nxt = min(range(len(remaining)), key=lambda i: distance(last, remaining[i]))
        route.append(remaining.pop(nxt))
    return route


def load_routes_for_day(day):
    """
    Возвращает список маршрутов (5 машин) на конкретный день.
    Каждый маршрут — список точек [lat, lon] в порядке объезда.
    """
    if os.path.exists('routes.json'):
        with open('routes.json', encoding='utf-8') as f:
            data = json.load(f)
        day_blocks = [b for b in data if b.get('day', day) == day]
        day_blocks.sort(key=lambda b: b.get('car', 0))
        routes = []
        for block in day_blocks:
            stops = block.get('stops', [])
            coords = [[p[0], p[1]] if isinstance(p, list) else [p['lat'], p['lon']] for p in stops]
            routes.append(coords)
        return routes

    # Демо (нет routes.json)
    points = [[a.lat, a.lon] for a in atms]
    clusters = kmeans_5(points, k=5)
    return [nearest_neighbor_order(c) for c in clusters]


def add_legend(m):
    """Добавляет легенду с пояснением цветов риска в правый нижний угол карты."""
    legend_html = '''
    <div style="position: fixed; 
                bottom: 30px; right: 30px; 
                background-color: white; 
                border: 2px solid #ccc; 
                border-radius: 8px; 
                padding: 10px 15px; 
                z-index: 1000;
                font-family: Arial, sans-serif;
                font-size: 14px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
        <strong>Уровень риска банкомата</strong><br>
        <span style="background-color: #2ecc71; width: 20px; height: 20px; display: inline-block; border-radius: 50%; margin-right: 8px;"></span> Зелёный — норма<br>
        <span style="background-color: #f1c40f; width: 20px; height: 20px; display: inline-block; border-radius: 50%; margin-right: 8px;"></span> Жёлтый — внимание (заполнение >70% или выдача <30%)<br>
        <span style="background-color: #e74c3c; width: 20px; height: 20px; display: inline-block; border-radius: 50%; margin-right: 8px;"></span> Красный — критично (>90% приёма или <10% выдачи)
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))


def build_map_for_day(day):
    # Сброс всех банкоматов в начальное состояние
    for atm in atms:
        atm.current_in = 0
        atm.current_out = atm.capacity_out

    # Загружаем routes.json
    if os.path.exists('routes.json'):
        with open('routes.json', encoding='utf-8') as f:
            all_routes = json.load(f)
    else:
        all_routes = []

    # Симулируем дни по порядку с учётом объезда
    for d in range(1, day + 1):
        if d > 1:
            for atm in atms:
                atm.update_levels(24)

        # Сбрасываем бункеры объезженных банкоматов в этот день
        day_stops = set()
        for block in all_routes:
            if block.get('day') == d:
                for stop in block.get('stops', []):
                    day_stops.add((round(stop[0], 6), round(stop[1], 6)))

        for atm in atms:
            key = (round(atm.lat, 6), round(atm.lon, 6))
            if key in day_stops:
                atm.current_in = 0
                atm.current_out = atm.capacity_out

    m = folium.Map(location=[55.75, 37.62], zoom_start=11)

    for atm in atms:
        risk = atm.get_risk_level(hours_ahead=24)
        color = risk_colors.get(risk, '#279ed1')
        folium.CircleMarker(
            location=[atm.lat, atm.lon],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"ID: {atm.id} | Риск: {risk}"
        ).add_to(m)

    routes = load_routes_for_day(day)
    for i, route_coords in enumerate(routes[:5]):
        if not route_coords:
            continue
        folium.PolyLine(
            route_coords,
            color=route_colors[i],
            weight=3,
            opacity=0.8,
            popup=f"{route_names[i]} (день {day})"
        ).add_to(m)

    add_legend(m)

    output_dir = 'templates'
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f'map_day{day}.html')
    m.save(filename)
    print(f"Карта дня {day} готова: {filename} (банкоматы раскрашены по риску, легенда добавлена)")
