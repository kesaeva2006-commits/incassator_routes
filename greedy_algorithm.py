import networkx as nx
from atm import Atm
from map_loader import load_moscow_graph
from node_matcher import match_atms_to_nodes
from route_utils import calculate_travel_time


def travel_time_between(a: Atm, b: Atm, G, atm_to_node: dict) -> float:
    """
    Считает реальное время в пути между двумя банкоматами по дорожному графу.
    :param a: первый банкомат
    :param b: второй банкомат
    :param G: граф дорог (networkx)
    :param atm_to_node: словарь соответствия банкомат → ближайший узел графа
    :return: время в секундах (или бесконечность, если путь не найден)
    """
    # Получаем узлы графа (перекрёстки), к которым привязаны банкоматы
    node_a = atm_to_node[a.id]
    node_b = atm_to_node[b.id]
    try:
        # Ищем кратчайший путь между узлами по времени
        # weight='travel_time' означает, что учитывается именно время, а не длина дороги
        return nx.shortest_path_length(G, node_a, node_b, weight='travel_time')
    except nx.NetworkXNoPath:
        # Если между точками нет пути (например, разрыв графа),
        # возвращаем бесконечность — такой маршрут не будет выбран
        return float('inf')


def nearest_neighbor_route(atms: list[Atm], start_atm: Atm | None = None,
                           use_graph: bool = True) -> list[Atm]:
    """
    Строит маршрут обхода банкоматов жадным алгоритмом (метод ближайшего соседа).

    Поддерживает два режима расчёта времени между банкоматами:

    1) use_graph=True (по умолчанию) — ТОЧНЫЙ режим.
       Реальное время движения по дорогам Москвы через граф OSMnx
       (load_moscow_graph + кратчайший путь по travel_time).
       Используется локально, где граф уже скачан в кэш moscow_graph.pkl.

    2) use_graph=False — БЫСТРЫЙ режим (для автосборки в GitHub Actions).
       Время оценивается по географическому расстоянию через
       route_utils.calculate_travel_time (формула гаверсинусов + коэффициент
       извилистости дорог). НЕ требует скачивания графа Москвы, поэтому
       работает за секунды в чистом окружении CI.

    Интерфейс функции сохранён прежним — старый код, вызывающий
    nearest_neighbor_route(atms) или nearest_neighbor_route(atms, start), работает
    без изменений (по умолчанию используется точный режим с графом).

    :param atms: список банкоматов
    :param start_atm: начальный банкомат (если не задан — берётся первый)
    :param use_graph: True — по дорогам (OSMnx), False — по расстоянию (быстро)
    :return: список банкоматов в порядке обхода
    """
    # Если список пустой — возвращаем пустой маршрут
    if not atms:
        return []

    # Подготовка функции расчёта времени в зависимости от режима
    if use_graph:
        # Точный режим: загружаем граф дорог Москвы (из кэша или скачиваем)
        G = load_moscow_graph()
        # Привязываем каждый банкомат к ближайшему узлу графа (перекрёстку)
        atm_to_node = match_atms_to_nodes(atms)

        def time_to(current, candidate):
            return travel_time_between(current, candidate, G, atm_to_node)
    else:
        # Быстрый режим: время по географическому расстоянию, без графа
        def time_to(current, candidate):
            return calculate_travel_time(current, candidate)

    # Копируем список банкоматов, чтобы не изменять исходный
    unvisited = atms.copy()

    # Определяем стартовую точку маршрута
    if start_atm:
        current = start_atm
        unvisited.remove(start_atm)
    else:
        # Если старт не задан — берём первый банкомат
        current = unvisited.pop(0)

    # Начинаем маршрут с текущего банкомата
    route = [current]

    # Пока есть непосещённые банкоматы
    while unvisited:
        # Выбираем банкомат с минимальным временем поездки от текущего (жадный выбор)
        nearest = min(unvisited, key=lambda atm: time_to(current, atm))
        # Добавляем его в маршрут
        route.append(nearest)
        # Удаляем из списка непосещённых
        unvisited.remove(nearest)
        # Переходим к нему — он становится текущим
        current = nearest

    # Возвращаем готовый маршрут
    return route
