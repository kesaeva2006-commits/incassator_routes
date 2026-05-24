import networkx as nx
from atm import Atm
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
    node_a = atm_to_node[a.id]
    node_b = atm_to_node[b.id]
    try:
        return nx.shortest_path_length(G, node_a, node_b, weight='travel_time')
    except nx.NetworkXNoPath:
        return float('inf')


def nearest_neighbor_route(atms: list[Atm], start_atm: Atm | None = None,
                           use_graph: bool = True) -> list[Atm]:
    """
    Строит маршрут обхода банкоматов жадным алгоритмом.

    use_graph=True (по умолчанию) — точный расчёт по дорогам (OSMnx)
    use_graph=False — быстрый расчёт по расстоянию (для CI)
    """
    if not atms:
        return []

    # Подготовка функции расчёта времени
    if use_graph:
        # Точный режим: импортируем ТОЛЬКО при необходимости
        from map_loader import load_moscow_graph
        from node_matcher import match_atms_to_nodes
        
        G = load_moscow_graph()
        atm_to_node = match_atms_to_nodes(atms)
        
        def time_to(current, candidate):
            return travel_time_between(current, candidate, G, atm_to_node)
    else:
        # Быстрый режим: без графа
        def time_to(current, candidate):
            return calculate_travel_time(current, candidate)

    # Жадный алгоритм
    unvisited = atms.copy()
    if start_atm:
        current = start_atm
        unvisited.remove(start_atm)
    else:
        current = unvisited.pop(0)

    route = [current]
    while unvisited:
        nearest = min(unvisited, key=lambda atm: time_to(current, atm))
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    return route
