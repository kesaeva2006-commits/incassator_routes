"""
build_routes.py — сборщик маршрутов для автоматической сборки в GitHub Actions.

Берёт банкоматы из atms.json, делит на 5 групп (по машине), строит маршрут
объезда в каждой группе на каждый из 3 дней и сохраняет в routes.json в формате,
который читает generate_map.py и index.html:

    [{"day": 1, "car": 1, "stops": [[lat, lon], ...], "critical_count": 5, "total_time": 320.5}, ...]

Псевдокод главной логики:
    загрузить 1000 банкоматов из atms.json
    загрузить граф дорог Москвы (один раз)
    привязать каждый банкомат к ближайшему перекрёстку (один раз)
    
    для каждого дня (1, 2, 3):
        если день > 1: обновить уровни бункеров на 24 часа
        разделить банкоматы на 5 кластеров по географии
        для каждого кластера:
            отобрать только RED и YELLOW банкоматы
            построить маршрут жадным алгоритмом по реальным дорогам
            обрезать маршрут если превышает 8 часов
            сбросить бункеры объезженных банкоматов (они обслужены)
        сохранить маршруты дня в routes.json
"""

import json
from atm import Atm
from clustering import cluster_atms
from greedy_algorithm import nearest_neighbor_route, travel_time_between

DAYS = 3       # количество дней планирования
N_CARS = 5     # количество машин инкассаторов
ATMS_FILE = 'atms.json'
ROUTES_FILE = 'routes.json'


def load_atms_from_json(path):
    """
    Читает atms.json и превращает каждую запись в объект Atm.
    
    Псевдокод:
        открыть файл
        для каждой записи → создать объект Atm с параметрами
        вернуть список объектов
    """
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
    """
    Возвращает числовой приоритет для сортировки банкоматов внутри маршрута.
    RED = 0 (первыми), YELLOW = 1, GREEN = 2 (не попадают в маршрут).
    
    Псевдокод:
        если риск RED → вернуть 0
        если риск YELLOW → вернуть 1
        иначе → вернуть 2
    """
    risk = atm.get_risk_level()
    if risk == 'RED':
        return 0
    if risk == 'YELLOW':
        return 1
    return 2


def route_total_minutes(route, G, atm_to_node):
    """
    Считает суммарное время прохождения маршрута в минутах.
    Использует реальное дорожное время через граф OSMnx (Дейкстра).
    Добавляет время обслуживания каждого банкомата (15 мин) и резерв (30 мин).
    
    Псевдокод:
        если маршрут пустой или 1 банкомат → вернуть 0
        для каждой пары соседних банкоматов → взять время по дорогам
        суммировать время в пути (секунды → минуты)
        добавить обслуживание + резерв через check_workday_limit
        вернуть итог
    """
    if len(route) < 2:
        return 0.0

    total_sec = 0.0
    for a, b in zip(route, route[1:]):
        # travel_time_between возвращает секунды по кратчайшему пути через граф
        t = travel_time_between(a, b, G, atm_to_node)
        if t != float('inf'):
            total_sec += t

    # Переводим секунды в минуты
    travel_min = total_sec / 60.0

    # check_workday_limit добавляет 15 мин на каждый банкомат + 30 мин резерв
    from route_utils import check_workday_limit
    _, total = check_workday_limit(route, travel_time=travel_min)
    return round(total, 1)


def build_one_day(atms, day, G, atm_to_node):
    """
    Строит маршруты инкассации на один день.

    atms - список банкоматов
    day - номер дня (если >1, обновляем уровни)
    G - граф дорог
    atm_to_node - соответствие ATM -> узел графа
    """

    from route_utils import trim_route_by_time, calculate_travel_time

    #  Если это не первый день — обновляем состояние банкоматов (накопление денег)
    if day > 1:
        for atm in atms:
            atm.update_levels(24)  # обновление за 24 часа

    #  Делим банкоматы на кластеры (по числу машин)
    clusters = cluster_atms(atms, n_clusters=N_CARS)

    routes = []            # итоговые маршруты
    critical_counts = []   # сколько критичных банкоматов обслужено
    times = []             # время маршрутов

    #  Обрабатываем каждый кластер (каждую машину)
    for cluster in clusters:

        #  Выбираем только срочные банкоматы (RED и YELLOW)
        urgent = [atm for atm in cluster if atm.get_risk_level() in ('RED', 'YELLOW')]

        #  Если срочных меньше 2 — просто берём как есть
        if len(urgent) < 2:
            route = list(urgent)

        else:
            #  Сортируем по приоритету (например, по степени переполнения)
            sorted_urgent = sorted(urgent, key=get_priority)

            #  Строим маршрут методом ближайшего соседа (жадный алгоритм)
            route = nearest_neighbor_route(sorted_urgent, use_graph=True)

            # ⏱ Считаем время между точками (по прямой, не по графу)
            travel_times = [
                calculate_travel_time(route[i-1], route[i])
                for i in range(1, len(route))
            ]

            #  Обрезаем маршрут, если превышает 8 часов
            route = trim_route_by_time(route, travel_times)

        #  После посещения банкомата — "обнуляем" вход и заполняем выдачу
        for atm in route:
            atm.current_in = 0
            atm.current_out = atm.capacity_out

        #  Сохраняем результаты
        routes.append(route)

        # сколько банкоматов обслужили
        critical_counts.append(len(route))

        #  реальное время маршрута по графу дорог
        times.append(route_total_minutes(route, G, atm_to_node))

    return routes, critical_counts, times


def main():
    """
    Главная функция — оркестрирует весь процесс построения маршрутов.
    
    Псевдокод:
        загрузить банкоматы из atms.json
        загрузить граф дорог Москвы ОДИН РАЗ (кэш moscow_graph.pkl)
        привязать банкоматы к узлам графа ОДИН РАЗ
        инициализировать банкоматы (бункеры в начальном состоянии)
        для каждого дня (1, 2, 3):
            построить маршруты
            сохранить в список результатов
        записать все результаты в routes.json
    """
    from map_loader import load_moscow_graph
    from node_matcher import match_atms_to_nodes

    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    # Загружаем граф дорог Москвы один раз — он используется все 3 дня
    # Если есть кэш (moscow_graph.pkl) — загрузка займёт секунды
    G = load_moscow_graph()

    # Создаём список банкоматов который живёт все 3 дня
    # Состояние бункеров переносится между днями — объезд дня 1 влияет на день 2
    atms_live = []
    for atm in atms:
        a = Atm(
            atm_id=atm.id, lat=atm.lat, lon=atm.lon,
            capacity_in=atm.capacity_in, capacity_out=atm.capacity_out,
            mean_in=atm.mean_in, std_in=atm.std_in,
            mean_out=atm.mean_out, std_out=atm.std_out,
        )
        # Начальное состояние: бункер приёма пуст, бункер выдачи полон
        a.current_in = 0
        a.current_out = a.capacity_out
        atms_live.append(a)

    # Привязываем банкоматы к ближайшим перекрёсткам графа — один раз для всех дней
    atm_to_node = match_atms_to_nodes(atms_live, G)

    result = []
    for day in range(1, DAYS + 1):
        print(f"Строю маршруты на день {day} ...")
        day_routes, day_critical_counts, day_times = build_one_day(
            atms_live, day, G, atm_to_node
        )

        # Сохраняем каждый маршрут (машина + день) в список результатов
        for car_index, (route, critical_count, total_time) in enumerate(
                zip(day_routes, day_critical_counts, day_times), start=1):
            stops = [[atm.lat, atm.lon] for atm in route]
            result.append({
                'day': day,
                'car': car_index,
                'stops': stops,              # координаты банкоматов маршрута
                'critical_count': critical_count,  # сколько критических объехали
                'total_time': total_time     # суммарное время маршрута в минутах
            })

    # Записываем все маршруты в routes.json
    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nГотово. Сохранено в {ROUTES_FILE}: {len(result)} маршрутов")
    for block in result:
        print(f"  День {block['day']}, машина {block['car']}: "
              f"{len(block['stops'])} банкоматов, "
              f"критических: {block.get('critical_count', 0)}, "
              f"время: {block.get('total_time', 0)} мин")


if __name__ == '__main__':
    main()
