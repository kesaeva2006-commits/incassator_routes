"""
build_routes.py — сборщик маршрутов для автоматической сборки в GitHub Actions.

Берёт банкоматы из atms.json, делит на 5 групп (по машине), строит маршрут
объезда в каждой группе на каждый из 3 дней и сохраняет в routes.json в формате,
который читает generate_map.py и index.html:

    [{"day": 1, "car": 1, "stops": [[lat, lon], ...], "critical_count": 5}, ...]

Маршруты строятся функцией алгоритмиста nearest_neighbor_route в ТОЧНОМ режиме
(use_graph=True): время между банкоматами считается по реальной дорожной сети
Москвы (OSMnx) через матрицу времён. Объезжаются только критические банкоматы
(RED и YELLOW), зелёные пропускаются.

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
    Обновляет уровни банкоматов до этого дня, затем кластеризует, сортирует по приоритету
    и строит маршруты.
    """
    # 1. Обновляем уровни банкоматов до начала этого дня
    hours_passed = 24 * (day - 1)
    for atm in atms:
        atm.current_in = 0
        atm.current_out = atm.capacity_out
        atm.update_levels(hours_passed)
    
    # 2. Кластеризуем (делим на 5 групп по географической близости)
    clusters = cluster_atms(atms, n_clusters=N_CARS)
    
    # 3. Для каждого кластера строим маршрут с учётом приоритетов
    routes = []
    critical_counts = []
    for cluster in clusters:
        # оставляем только критические (RED и YELLOW), зелёные пропускаем
        urgent = [atm for atm in cluster if atm.get_risk_level() in ('RED', 'YELLOW')]
        if len(urgent) < 2:
            route = list(urgent)
        else:
            sorted_urgent = sorted(urgent, key=get_priority)  # красные раньше жёлтых
            route = nearest_neighbor_route(sorted_urgent, use_graph=True)
        routes.append(route)
        critical_counts.append(len(route))  # все в маршруте критические
    
    return routes, critical_counts


def main():
    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    # Сохраняем исходное состояние (для сброса между днями)
    original_atms = []
    for atm in atms:
        original_atms.append(Atm(
            atm_id=atm.id,
            lat=atm.lat,
            lon=atm.lon,
            capacity_in=atm.capacity_in,
            capacity_out=atm.capacity_out,
            mean_in=atm.mean_in,
            std_in=atm.std_in,
            mean_out=atm.mean_out,
            std_out=atm.std_out,
        ))
        original_atms[-1].current_in = 0
        original_atms[-1].current_out = original_atms[-1].capacity_out

    result = []
    for day in range(1, DAYS + 1):
        print(f"Строю маршруты на день {day} ...")
        
        # Копируем исходное состояние для этого дня
        atms_copy = []
        for atm in original_atms:
            atms_copy.append(Atm(
                atm_id=atm.id,
                lat=atm.lat,
                lon=atm.lon,
                capacity_in=atm.capacity_in,
                capacity_out=atm.capacity_out,
                mean_in=atm.mean_in,
                std_in=atm.std_in,
                mean_out=atm.mean_out,
                std_out=atm.std_out,
            ))
            atms_copy[-1].current_in = 0
            atms_copy[-1].current_out = atms_copy[-1].capacity_out
        
        day_routes, day_critical_counts = build_one_day(atms_copy, day)
        
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
