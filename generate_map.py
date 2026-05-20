import folium
import requests
import json
import os

#  Генерация карты Москвы: 1000 банкоматов + 5 маршрутов
#  Frontend, Спринт 3 — отображение 5 маршрутов разными цветами

# 1. Загрузка банкоматов (данные от Лилии)
url = 'https://raw.githubusercontent.com/kesaeva2006-commits/incassator_routes/feature/backend/atms.json'
response = requests.get(url)
atms = response.json()

# 2. Создание карты Москвы
m = folium.Map(location=[55.75, 37.62], zoom_start=11)

# 3. Точки банкоматов (как было)
for atm in atms:
    folium.CircleMarker(
        location=[atm['lat'], atm['lon']],
        radius=3,
        color='#279ed1',
        fill=True,
        fill_color='#279ed1',
        popup=f"ID: {atm['id']}"
    ).add_to(m)

# 4. Получение маршрутов для 5 машин
# Цвета и названия 5 машин-инкассаторов
colors = ['red', 'blue', 'green', 'orange', 'purple']
names = ['Машина 1', 'Машина 2', 'Машина 3', 'Машина 4', 'Машина 5']


def load_routes():
    """
    Возвращает список из 5 маршрутов. Каждый маршрут — список точек [lat, lon]
    в порядке объезда.

    Источник данных:
      1) routes.json от алгоритмистов/бэкенда (если файл есть) — реальные маршруты;
      2) если файла нет — демо-маршруты: банкоматы делятся на 5 групп по близости.
         Когда появится routes.json, отрисовка реальных маршрутов заработает
         автоматически, без изменения кода ниже.
    """
    # Вариант 1: реальные маршруты из routes.json
    if os.path.exists('routes.json'):
        with open('routes.json', encoding='utf-8') as f:
            data = json.load(f)
        routes = []
        for item in data:
            # Поддерживаем формат {"car": 1, "stops": [[lat, lon], ...]}
            stops = item.get('stops', item) if isinstance(item, dict) else item
            coords = [[p['lat'], p['lon']] if isinstance(p, dict) else p for p in stops]
            routes.append(coords)
        print("Маршруты загружены из routes.json")
        return routes

    # Вариант 2: демо-маршруты (пока нет routes.json)
    print("routes.json не найден — рисуем демо-маршруты (5 групп)")
    # Сортируем банкоматы по широте, чтобы линии шли упорядоченно, а не хаосом
    atms_sorted = sorted(atms, key=lambda a: (a['lat'], a['lon']))
    routes = []
    group_size = len(atms_sorted) // 5
    for i in range(5):
        start = i * group_size
        end = (i + 1) * group_size if i < 4 else len(atms_sorted)
        group = atms_sorted[start:end]
        coords = [[a['lat'], a['lon']] for a in group]
        routes.append(coords)
    return routes


# 5. Отрисовка 5 маршрутов разными цветами
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
