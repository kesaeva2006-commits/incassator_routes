import json
from atm import Atm
from clustering import cluster_atms
from greedy_algorithm import nearest_neighbor_route, travel_time_between, build_time_matrix

DAYS = 3
N_CARS = 5
ATMS_FILE = 'atms.json'
ROUTES_FILE = 'routes.json'


def load_atms_from_json(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    atms = []
    for item in data:
        atms.append(Atm(
            atm_id=item['id'], lat=item['lat'], lon=item['lon'],
            capacity_in=item['capacity_in'], capacity_out=item['capacity_out'],
            mean_in=item.get('mean_in', 0), std_in=item.get('std_in', 0),
            mean_out=item.get('mean_out', 0), std_out=item.get('std_out', 0),
        ))
    return atms


def get_priority(atm):
    risk = atm.get_risk_level()
    if risk == 'RED': return 0
    if risk == 'YELLOW': return 1
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


def trim_route_by_graph(route, G, atm_to_node, service_time=15, reserve=30):
    WORKDAY_MINUTES = 480
    if len(route) < 2:
        return route
    sub_atm_to_node = {atm.id: atm_to_node[atm.id] for atm in route if atm.id in atm_to_node}
    matrix = build_time_matrix(route, G, sub_atm_to_node)
    accumulated = reserve
    trimmed = []
    for i, atm in enumerate(route):
        if i > 0:
            t = matrix.get((route[i-1].id, atm.id), 0) / 60
            accumulated += t
        accumulated += service_time
        if accumulated > WORKDAY_MINUTES:
            break
        trimmed.append(atm)
    return trimmed


def build_one_day(atms, day, G, atm_to_node):
    # Обновляем уровни на 24 часа (кроме первого дня)
    if day > 1:
        for atm in atms:
            atm.update_levels(24)

    clusters = cluster_atms(atms, n_clusters=N_CARS)
    routes = []
    critical_counts = []
    times = []

    for cluster in clusters:
        urgent = [atm for atm in cluster if atm.get_risk_level() in ('RED', 'YELLOW')]
        if len(urgent) < 2:
            route = list(urgent)
        else:
            sorted_urgent = sorted(urgent, key=get_priority)
            route = nearest_neighbor_route(sorted_urgent, use_graph=True)
            route = trim_route_by_graph(route, G, atm_to_node)

        # После объезда сбрасываем бункеры — банкомат становится зелёным
        for atm in route:
            atm.current_in = 0
            atm.current_out = atm.capacity_out

        routes.append(route)
        critical_counts.append(len(route))
        times.append(route_total_minutes(route, G, atm_to_node))

    return routes, critical_counts, times


def main():
    from map_loader import load_moscow_graph
    from node_matcher import match_atms_to_nodes

    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    G = load_moscow_graph()

    # Один список банкоматов на все 3 дня — состояние переносится между днями
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
    for day in range(1, DAYS + 1):
        print(f"Строю маршруты на день {day} ...")
        day_routes, day_critical_counts, day_times = build_one_day(atms_live, day, G, atm_to_node)

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
