"""
build_routes.py — сборщик маршрутов для автоматической сборки в GitHub Actions.
"""

import json
from atm import Atm
from clustering import cluster_atms
from greedy_algorithm import nearest_neighbor_route, travel_time_between

DAYS = 3
N_CARS = 5
ATMS_FILE = 'atms.json'
ROUTES_FILE = 'routes.json'
WORKDAY_MINUTES = 480


def load_atms_from_json(path):
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
    risk = atm.get_risk_level()
    if risk == 'RED':
        return 0
    if risk == 'YELLOW':
        return 1
    return 2


def trim_route_by_graph(route, G, atm_to_node, service_time=15, reserve=30):
    """Обрезает маршрут если превышает 8 часов по реальному времени."""
    accumulated = reserve
    for i, atm in enumerate(route):
        if i > 0:
            t_sec = travel_time_between(route[i-1], atm, G, atm_to_node)
            if t_sec == float('inf'):
                t_sec = 0
            accumulated += t_sec / 60.0
        accumulated += service_time
        if accumulated > WORKDAY_MINUTES:
            return route[:i]
    return route


def route_total_minutes(route, G, atm_to_node):
    """Суммарное время маршрута в минутах по реальным дорогам."""
    if len(route) < 2:
        return 0.0
    from route_utils import check_workday_limit
    total_sec = 0.0
    for a, b in zip(route, route[1:]):
        t = travel_time_between(a, b, G, atm_to_node)
        if t != float('inf'):
            total_sec += t
    travel_min = total_sec / 60.0
    _, total = check_workday_limit(route, travel_time=travel_min)
    return round(total, 1)


def build_one_day(atms, day, G, match_atms_to_nodes_fn):
    """Строит маршруты для конкретного дня."""
    clusters = cluster_atms(atms, n_clusters=N_CARS)
    routes = []
    critical_counts = []
    times = []

    for cluster in clusters:
        urgent = [atm for atm in cluster if atm.get_risk_level(hours_ahead=24) in ('RED', 'YELLOW')]

        if len(urgent) < 2:
            route = list(urgent)
            atm_to_node = match_atms_to_nodes_fn(route, G=G) if route else {}
        else:
            sorted_urgent = sorted(urgent, key=get_priority)
            atm_to_node = match_atms_to_nodes_fn(sorted_urgent, G=G)
            route = nearest_neighbor_route(sorted_urgent, use_graph=True, G=G, atm_to_node=atm_to_node)
            route = trim_route_by_graph(route, G, atm_to_node)

        routes.append(route)
        critical_counts.append(len(route))
        atm_to_node_full = match_atms_to_nodes_fn(route, G=G) if len(route) > 1 else {}
        times.append(route_total_minutes(route, G, atm_to_node_full))

    return routes, critical_counts, times


def main():
    from map_loader import load_moscow_graph
    from node_matcher import match_atms_to_nodes

    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    print("Загружаем граф дорог...")
    G = load_moscow_graph()

    serviced_ids = set()

    result = []
    for day in range(1, DAYS + 1):
        print(f"Строю маршруты на день {day} ...")

        atms_copy = []
        for atm in atms:
            new_atm = Atm(
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
            new_atm.current_in = 0
            new_atm.current_out = new_atm.capacity_out

            if atm.id in serviced_ids:
                # Обслуженный — сброшен и накопил только 24ч
                new_atm.update_levels(24)
            else:
                # Необслуженный — накапливался с начала
                new_atm.update_levels(24 * (day - 1))

            atms_copy.append(new_atm)

        day_routes, day_critical_counts, day_times = build_one_day(
            atms_copy, day, G, match_atms_to_nodes
        )

        # Запоминаем обслуженные банкоматы
        for route in day_routes:
            for atm in route:
                serviced_ids.add(atm.id)

        for car_index, (route, critical_count, total_time) in enumerate(
                zip(day_routes, day_critical_counts, day_times), start=1):
            stops = [[atm.lat, atm.lon] for atm in route]
            result.append({
                'day': day,
                'car': car_index,
                'stops': stops,
                'critical_count': critical_count,
                'total_time': total_time
            })

    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nГотово. Сохранено в {ROUTES_FILE}: {len(result)} маршрутов")
    for block in result:
        print(f"  День {block['day']}, машина {block['car']}: "
              f"{len(block['stops'])} банкоматов, критических: {block.get('critical_count', 0)}")


if __name__ == '__main__':
    main()
