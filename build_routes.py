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

def route_total_minutes(route, use_graph=True):
    """Суммарное время прохождения готового маршрута, в минутах.
    В графовом режиме берём реальное дорожное время (Дейкстра, секунды)."""
    if len(route) < 2:
        return 0.0
    if use_graph:
        from map_loader import load_moscow_graph
        from node_matcher import match_atms_to_nodes
        G = load_moscow_graph()
        atm_to_node = match_atms_to_nodes(route)
        total_sec = 0.0
        for a, b in zip(route, route[1:]):
            t = travel_time_between(a, b, G, atm_to_node)
            if t != float('inf'):
                total_sec += t
        travel_min = total_sec / 60.0
        from route_utils import check_workday_limit
        _, total = check_workday_limit(route, travel_time=travel_min)
        return round(total, 1)
    else:
        from route_utils import calculate_travel_time
        return round(sum(calculate_travel_time(a, b)
                         for a, b in zip(route, route[1:])), 1)

def build_one_day(atms, day):
    """
    Строит маршруты для конкретного дня.
    Обновляет уровни банкоматов до этого дня, затем кластеризует,
    отсеивает зелёные банкоматы и строит маршруты только для критических.
    """
    # 1. Обновляем уровни банкоматов до начала этого дня
    hours_passed = 24 * (day - 1)
    for atm in atms:
        atm.current_in = 0
        atm.current_out = atm.capacity_out
        atm.update_levels(hours_passed)

    # 2. Кластеризуем (делим на 5 групп по географической близости)
    clusters = cluster_atms(atms, n_clusters=N_CARS)

    # 3. Для каждого кластера строим маршрут только из критических банкоматов
    routes = []
    critical_counts = []
    times = []
    for cluster in clusters:
        # Оставляем только критические (RED и YELLOW), зелёные пропускаем
        urgent = [atm for atm in cluster if atm.get_risk_level(hours_ahead=24) in ('RED', 'YELLOW')]
        if len(urgent) < 2:
            route = list(urgent)
        else:
            # Красные раньше жёлтых
            sorted_urgent = sorted(urgent, key=get_priority)
            route = nearest_neighbor_route(sorted_urgent, use_graph=True)
        routes.append(route)
        critical_counts.append(len(route))
        times.append(route_total_minutes(route, use_graph=True))

    return routes, critical_counts, times


def main():
    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    # Создаём словарь банкоматов по id для быстрого доступа
    atm_dict = {atm.id: atm for atm in atms}

    # Множество id банкоматов которые уже обслужили
    serviced_ids = set()

    result = []
    for day in range(1, DAYS + 1):
        print(f"Строю маршруты на день {day} ...")

        # Копируем банкоматы для этого дня
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

            # Если банкомат уже обслужили — сбрасываем его уровни в ноль
            # (инкассатор забрал деньги и пополнил бункер выдачи)
            if atm.id in serviced_ids:
                new_atm.current_in = 0
                new_atm.current_out = new_atm.capacity_out
                # Обновляем только за один день после обслуживания
                new_atm.update_levels(24)
            else:
                # Не обслуженный — накапливается с самого начала
                new_atm.update_levels(24 * (day - 1))

            atms_copy.append(new_atm)

        day_routes, day_critical_counts, day_times = build_one_day(atms_copy, day)

        # Запоминаем какие банкоматы обслужили сегодня
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
