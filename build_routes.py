"""
build_routes.py — сборщик маршрутов для автоматической сборки в GitHub Actions.

Берёт банкоматы из atms.json, делит на 5 групп (по машине), строит маршрут
объезда в каждой группе на каждый из 3 дней и сохраняет в routes.json в формате,
который читает generate_map.py и index.html:

    [{"day": 1, "car": 1, "stops": [[lat, lon], ...], "critical_count": 5}, ...]

Маршруты строятся функцией алгоритмиста nearest_neighbor_route в ТОЧНОМ режиме
(use_graph=True): время между банкоматами рассчитывается по реальным дорогам
Москвы через граф OSMnx и алгоритм Дейкстры. Требует наличия кэша карты
moscow_graph.pkl на диске. Для запуска в GitHub Actions без локального кэша
используйте use_graph=False — быстрый режим по географическому расстоянию.

Запускается автоматически в GitHub Actions — локально запускать не нужно.
"""

import json
from atm import Atm
from clustering import cluster_atms
from greedy_algorithm import nearest_neighbor_route, travel_time_between
from route_checker import check_all_routes, rebalance_clusters

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

def route_total_minutes(route, G, atm_to_node):
    if len(route) < 2:
        return 0.0
    total_sec = 0.0
    for a, b in zip(route, route[1:]):
        t = travel_time_between(a, b, G, atm_to_node)
        if t != float('inf'):
            total_sec += t
    travel_min = total_sec / 60.0
    from route_utils import check_workday_limit
    _, total = check_workday_limit(route, travel_time=travel_min)
    return round(total, 1)

def build_one_day(atms, day, G, atm_to_node, prev_day_visited=None):
    # 1. Сначала сбрасываем объезженные вчера
    if prev_day_visited:
        for atm in prev_day_visited:
            atm.current_in = 0
            atm.current_out = atm.capacity_out

    # 2. Потом обновляем уровни (прошли сутки)
    if day > 1:
        for atm in atms:
            atm.update_levels(24)

    # 3. Кластеризуем и строим маршруты
    clusters = cluster_atms(atms, n_clusters=N_CARS)
    routes = []
    critical_counts = []
    times = []
    visited_today = []
    visited_ids = {atm.id for atm in (prev_day_visited or [])}

    for cluster in clusters:
        urgent = [atm for atm in cluster
                  if atm.get_risk_level() in ('RED', 'YELLOW')
                  and atm.id not in visited_ids]

        if len(urgent) < 2:
            route = list(urgent)
        else:
            sorted_urgent = sorted(urgent, key=get_priority)
            sub_atm_to_node = {atm.id: atm_to_node[atm.id] for atm in sorted_urgent if atm.id in atm_to_node}
            route = nearest_neighbor_route(sorted_urgent, use_graph=True, G=G, atm_to_node=sub_atm_to_node)

        visited_today.extend(route)
        routes.append(route)
        critical_counts.append(len(route))
        times.append(route_total_minutes(route, G, atm_to_node))
    
    # 4. Проверяем маршруты на 8 часов и перераспределяем если нужно
    check_result = check_all_routes(clusters, routes)
    if check_result["over_limit"]:
        clusters, routes, _ = rebalance_clusters(clusters, routes, check_result)
        # Пересчитываем critical_counts и times после перебалансировки
        critical_counts = [len(r) for r in routes]
        times = [route_total_minutes(r, G, atm_to_node) for r in routes]
        visited_today = [atm for route in routes for atm in route]

    return routes, critical_counts, times, visited_today

def main():
    from map_loader import load_moscow_graph
    from node_matcher import match_atms_to_nodes

    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    G = load_moscow_graph()

    atms_live = []
    for atm in atms:
        a = Atm(
            atm_id=atm.id, lat=atm.lat, lon=atm.lon,
            capacity_in=atm.capacity_in, capacity_out=atm.capacity_out,
            mean_in=atm.mean_in, std_in=atm.std_in,
            mean_out=atm.mean_out, std_out=atm.std_out,
        )
        a.current_in = 0
        a.current_out = a.capacity_out
        atms_live.append(a)

    atm_to_node = match_atms_to_nodes(atms_live, G)

    result = []
    visited_prev = None
    for day in range(1, DAYS + 1):
        print(f"Строю маршруты на день {day} ...")
        day_routes, day_critical_counts, day_times, visited_prev = build_one_day(
            atms_live, day, G, atm_to_node, prev_day_visited=visited_prev
        )
        print(f"  Объезжено сегодня: {len(visited_prev)} банкоматов, id первых 3: {[a.id for a in visited_prev[:3]]}")

        for car_index, (route, critical_count, total_time) in enumerate(
                zip(day_routes, day_critical_counts, day_times), start=1):
            stops = [[atm.lat, atm.lon] for atm in route]
            result.append({
                'day': day, 'car': car_index,
                'stops': stops,
                'critical_count': critical_count,
                'total_time': total_time
            })

    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nГотово. Сохранено в {ROUTES_FILE}: {len(result)} маршрутов")
    for block in result:
        print(f"  День {block['day']}, машина {block['car']}: "
              f"{len(block['stops'])} банкоматов, критических: {block.get('critical_count', 0)}, "
              f"время: {block.get('total_time', 0)} мин")

if __name__ == '__main__':
    main()
