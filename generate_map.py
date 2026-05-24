import folium
import requests
import json
import os
import random
import math

# ============================================================
#  Генерация карт Москвы: банкоматы + 5 маршрутов разными цветами
#  Для каждого дня создаётся отдельный файл: map_day1.html, map_day2.html, map_day3.html
#  Frontend — отображение 5 маршрутов цветами + переключение по дням (задача 3.9)
# ============================================================

# --- 1. Загрузка банкоматов (данные от backend) ---
url = 'https://raw.githubusercontent.com/kesaeva2006-commits/incassator_routes/feature/backend/atms.json'
response = requests.get(url)
atms = response.json()

# --- Цвета и названия 5 машин ---
colors = ['red', 'blue', 'green', 'orange', 'purple']
names = ['Машина 1', 'Машина 2', 'Машина 3', 'Машина 4', 'Машина 5']

# Сколько дней (карта на каждый день)
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

    Источник:
      1) routes.json (если есть) — реальные маршруты, фильтр по дню day;
      2) если файла нет — демо-маршруты (одинаковые для всех дней).
    """
    if os.path.exists('routes.json'):
        with open('routes.json', encoding='utf-8') as f:
            data = json.load(f)
        day_blocks = [b for b in data if b.get('day', day) == day]
        day_blocks.sort(key=lambda b: b.get('car', 0))
        routes = []
        for block in day_blocks:
            stops = block.get('stops', [])
            coords = [[p['lat'], p['lon']] if isinstance(p, dict) else p for p in stops]
            routes.append(coords)
        return routes

    # Демо (нет routes.json)
    points = [[a['lat'], a['lon']] for a in atms]
    clusters = kmeans_5(points, k=5)
    return [nearest_neighbor_order(c) for c in clusters]


def build_map_for_day(day):
    """Строит и сохраняет карту map_dayN.html для указанного дня."""
    m = folium.Map(location=[55.75, 37.62], zoom_start=11)

    # Точки банкоматов
    for atm in atms:
        folium.CircleMarker(
            location=[atm['lat'], atm['lon']],
            radius=3,
            color='#279ed1',
            fill=True,
            fill_color='#279ed1',
            popup=f"ID: {atm['id']}"
        ).add_to(m)

    # 5 маршрутов разными цветами
    routes = load_routes_for_day(day)
    for i, route_coords in enumerate(routes[:5]):
        if not route_coords:
            continue
        folium.PolyLine(
            route_coords,
            color=colors[i],
            weight=3,
            opacity=0.8,
            popup=f"{names[i]} (день {day})"
        ).add_to(m)

    filename = f'map_day{day}.html'
    m.save(filename)
    print(f"Карта дня {day} готова: {filename}")


# --- Генерируем карту для каждого дня ---
for day in range(1, DAYS + 1):
    build_map_for_day(day)

print("Все карты по дням готовы")
