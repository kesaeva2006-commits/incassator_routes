"""
build_routes.py — сборщик маршрутов для автоматической сборки в GitHub Actions.

Берёт банкоматы из atms.json, делит на 5 групп (по машине), строит маршрут
объезда в каждой группе на каждый из 3 дней и сохраняет в routes.json в формате,
который читает generate_map.py и index.html:

    [{"day": 1, "car": 1, "stops": [[lat, lon], ...], "critical_count": 5}, ...]

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


def get_priority(atm):
    """Возвращает числовой приоритет для сортировки: 0 — RED, 1 — YELLOW, 2 — GREEN."""
    risk = atm.get_risk_level()
    if risk == 'RED':
        return 0
    if risk == 'YELLOW':
        return 1
    return 2


def build_one_day(atms, day):
    """
    Строит маршруты для конкретного дня.
    Накапливает уровни за один день (не сбрасывает — состояние несётся из предыдущего дня),
    затем кластеризует, отфильтровывает зелёных, строит маршруты и сбрасывает
    бункеры обслуженных банкоматов.
    """
    # 1. Накапливаем уровни за один день
    # Состояние берётся из предыдущего дня — не сбрасываем в ноль
    for atm in atms:
        atm.update_levels(24)

    # 2. Кластеризуем (делим на 5 групп по географической близости)
    clusters = cluster_atms(atms, n_clusters=N_CARS)

    # 3. Для каждого кластера строим маршрут только из критических банкоматов
    routes = []
    critical_counts = []
    for cluster in clusters:
        # Оставляем только RED и YELLOW — зелёные сегодня не нужны
        urgent = [atm for atm in cluster if atm.get_risk_level() in ('RED', 'YELLOW')]
        if len(urgent) < 2:
            route = list(urgent)
        else:
            # Красные раньше жёлтых
            sorted_urgent = sorted(urgent, key=get_priority)
            route = nearest_neighbor_route(sorted_urgent, use_graph=False)

        # После объезда сбрасываем бункеры посещённых банкоматов
        for atm in route:
            atm.current_in = 0
            atm.current_out = atm.capacity_out

        routes.append(route)
        # Все в маршруте критические — critical_count равен длине маршрута
        critical_counts.append(len(route))

    return routes, critical_counts


def main():
    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    # Создаём один список банкоматов который живёт через все три дня
    # Состояние переносится между днями — объезд дня 1 влияет на день 2
    atms_live = []
    for atm in atms:
        a = Atm(
            atm_id=atm.id,
            lat=atm.lat,
            lon=atm.lon,
            capacity_in=atm.capacity_in,
            capacity_out=atm.capacity_out,
            mean_in=atm.mean_in,
            std_in=atm.std_in,
            mean_out=atm.mean_out,
            std_out=atm.std_out,
        )
        a.current_in = 0
        a.current_out = a.capacity_out
        atms_live.append(a)

    result = []
    for day in range(1, DAYS + 1):
        print(f"Строю маршруты на день {day} ...")
        day_routes, day_critical_counts = build_one_day(atms_live, day)

        for car_index, (route, critical_count) in enumerate(zip(day_routes, day_critical_counts), start=1):
            stops = [[atm.lat, atm.lon] for atm in route]
            result.append({
                'day': day,
                'car': car_index,
                'stops': stops,
                'critical_count': critical_count
            })

    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nГотово. Сохранено в {ROUTES_FILE}: {len(result)} маршрутов")
    for block in result:
        print(f"  День {block['day']}, машина {block['car']}: {len(block['stops'])} банкоматов, критических: {block.get('critical_count', 0)}")


if __name__ == '__main__':
    main()
