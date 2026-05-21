import folium
import requests
import json
import os
import random
import math

#  Генерация карты Москвы: 1000 банкоматов + 5 маршрутов
#  Frontend, Спринт 3 — отображение 5 маршрутов разными цветами

# --- 1. Загрузка банкоматов (данные от Лилии) ---
url = 'https://raw.githubusercontent.com/kesaeva2006-commits/incassator_routes/feature/backend/atms.json'
response = requests.get(url)
atms = response.json()

# --- 2. Создание карты Москвы ---
m = folium.Map(location=[55.75, 37.62], zoom_start=11)

# --- 3. Точки банкоматов (как было) ---
for atm in atms:
    folium.CircleMarker(
        location=[atm['lat'], atm['lon']],
        radius=3,
        color='#279ed1',
        fill=True,
        fill_color='#279ed1',
        popup=f"ID: {atm['id']}"
    ).add_to(m)

# --- 4. Цвета и названия 5 машин ---
colors = ['red', 'blue', 'green', 'orange', 'purple']
names = ['Машина 1', 'Машина 2', 'Машина 3', 'Машина 4', 'Машина 5']

# Какой день показываем на карте (пока есть только день 1)
DAY = 1


def distance(a, b):
    """Расстояние между двумя точками [lat, lon] (грубое, для группировки)."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def kmeans_5(points, k=5, iterations=20):
    """
    Простая кластеризация на k групп по координатам (на чистом Python).
    Используется ТОЛЬКО для демо, когда нет routes.json.
    """
    random.seed(42)
    centers = random.sample(points, k)
    clusters = [[] for _ in range(k)]
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
    """Упорядочивает точки методом 'ближайший сосед' (для демо)."""
    if not points:
        return []
    remaining = points[:]
    route = [remaining.pop(0)]
    while remaining:
        last = route[-1]
        nxt = min(range(len(remaining)), key=lambda i: distance(last, remaining[i]))
        route.append(remaining.pop(nxt))
    return route


def load_routes():
    """
    Возвращает список маршрутов на выбранный день DAY.
    Каждый маршрут — список точек [lat, lon] в порядке объезда.

    Источник данных:
      1) routes.json от алгоритмистов/бэкенда (если файл есть) — реальные маршруты;
         формат: [{"day": 1, "car": 1, "stops": [[lat, lon], ...]}, ...]
      2) если файла нет — демо (k-means + ближайший сосед).
    """
    # --- Вариант 1: реальные маршруты из routes.json ---
    if os.path.exists('routes.json'):
        with open('routes.json', encoding='utf-8') as f:
            data = json.load(f)

        # Берём только нужный день и сортируем по номеру машины (car)
        day_blocks = [b for b in data if b.get('day', DAY) == DAY]
        day_blocks.sort(key=lambda b: b.get('car', 0))

        routes = []
        for block in day_blocks:
            stops = block.get('stops', [])
            coords = [[p['lat'], p['lon']] if isinstance(p, dict) else p for p in stops]
            routes.append(coords)
        print(f"Маршруты загружены из routes.json (день {DAY}): {len(routes)} машин")
        return routes

    # --- Вариант 2: демо-маршруты (пока нет routes.json) ---
    print("routes.json не найден — рисуем демо-маршруты (5 районов)")
    points = [[a['lat'], a['lon']] for a in atms]
    clusters = kmeans_5(points, k=5)
    routes = [nearest_neighbor_order(cluster) for cluster in clusters]
    return routes


# --- 5. Отрисовка 5 маршрутов разными цветами ---
routes = load_routes()
for i, route_coords in enumerate(routes[:5]):
    if not route_coords:
        continue
    folium.PolyLine(
        route_coords,
        color=colors[i],
        weight=3,
        opacity=0.8,
        popup=names[i]
    ).add_to(m)

# --- 6. Сохранение карты ---
m.save('map.html')
print("Карта с банкоматами и 5 маршрутами готова")
