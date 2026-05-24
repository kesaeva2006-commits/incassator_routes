"""
build_routes.py — сборщик маршрутов для автоматической сборки в GitHub Actions.

Берёт банкоматы из atms.json, делит на 5 групп (по машине), строит маршрут
объезда в каждой группе на каждый из 3 дней и сохраняет в routes.json в формате,
который читает generate_map.py:

    [{"day": 1, "car": 1, "stops": [[lat, lon], ...]}, ...]

Маршруты строятся функцией алгоритмиста nearest_neighbor_route в БЫСТРОМ режиме
(use_graph=False): время между банкоматами оценивается по географическому
расстоянию (route_utils.calculate_travel_time), без скачивания графа дорог
OSMnx. Это позволяет собирать маршруты за секунды в чистом окружении GitHub
Actions. Точный режим по реальным дорогам (use_graph=True) доступен локально.

Запускается автоматически в GitHub Actions — локально запускать не нужно.
"""

import json
from atm import Atm
from clustering import cluster_atms
from greedy_algorithm import nearest_neighbor_route

DAYS = 3
N_CARS = 5
ATMS_FILE = 'atms.json'
ROUTES_FILE = 'routes.json'


def load_atms_from_json(path):
    """Читает atms.json и превращает каждую запись в объект Atm."""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    atms = []
    for item in data:
        atms.append(Atm(
            atm_id=item['id'],
            lat=item['lat'],
            lon=item['lon'],
            capacity_in=item['capacity_in'],
            capacity_out=item['capacity_out'],
            mean_in=item.get('mean_in', 0),
            std_in=item.get('std_in', 0),
            mean_out=item.get('mean_out', 0),
            std_out=item.get('std_out', 0),
        ))
    return atms


def build_one_day(atms):
    """Делит банкоматы на 5 групп и строит маршрут в каждой (быстрый режим, без OSMnx)."""
    clusters = cluster_atms(atms, n_clusters=N_CARS)
    routes = []
    for cluster in clusters:
        if len(cluster) >= 2:
            route = nearest_neighbor_route(cluster, use_graph=False)
        else:
            route = list(cluster)
        routes.append(route)
    return routes


def main():
    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    result = []
    for day in range(1, DAYS + 1):
        print(f"Строю маршруты на день {day} ...")
        day_routes = build_one_day(atms)
        for car_index, route in enumerate(day_routes, start=1):
            stops = [[atm.lat, atm.lon] for atm in route]
            result.append({'day': day, 'car': car_index, 'stops': stops})
        # Обновляем уровни бункеров для прогноза следующего дня
        for atm in atms:
            atm.update_levels(24)

    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nГотово. Сохранено в {ROUTES_FILE}: {len(result)} маршрутов")
    for block in result:
        print(f"  День {block['day']}, машина {block['car']}: {len(block['stops'])} банкоматов")


if __name__ == '__main__':
    main()
