import networkx as nx
from atm import Atm
from route_utils import calculate_travel_time


def travel_time_between(a: Atm, b: Atm, G, atm_to_node: dict) -> float:
    """
    Считает реальное время в пути между двумя банкоматами по дорожному графу.
    """
    node_a = atm_to_node[a.id]
    node_b = atm_to_node[b.id]
    try:
        return nx.shortest_path_length(G, node_a, node_b, weight='travel_time')
    except nx.NetworkXNoPath:
        return float('inf')


def build_time_matrix(atms, G, atm_to_node):
    """
    Строит матрицу времён между всеми парами банкоматов.
    Один запуск Дейкстры на каждый банкомат находит время до ВСЕХ остальных.
    Возвращает словарь: matrix[(id_a, id_b)] = время в секундах.
    """
    matrix = {}
    for atm in atms:
        source = atm_to_node[atm.id]
        lengths = nx.single_source_dijkstra_path_length(G, source, weight='travel_time')
        for other in atms:
            dest = atm_to_node[other.id]
            matrix[(atm.id, other.id)] = lengths.get(dest, float('inf'))
    return matrix


def nearest_neighbor_route_matrix(atms, G, atm_to_node):
    """
    Жадный маршрут с использованием готовой матрицы времён (быстро).
    """
    if not atms:
        return []
    matrix = build_time_matrix(atms, G, atm_to_node)
    unvisited = atms.copy()
    current = unvisited.pop(0)
    route = [current]
    while unvisited:
        nearest = min(unvisited, key=lambda a: matrix[(current.id, a.id)])
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    return route


def nearest_neighbor_route(atms: list[Atm], start_atm=None,
                           use_graph: bool = True, G=None, atm_to_node=None) -> list[Atm]:
    if not atms:
        return []
    if use_graph:
        from map_loader import load_moscow_graph
        from node_matcher import match_atms_to_nodes
        if G is None:
            G = load_moscow_graph()
        if atm_to_node is None:
            atm_to_node = match_atms_to_nodes(atms, G)
        return nearest_neighbor_route_matrix(atms, G, atm_to_node)
    else:
        def time_to(current, candidate):
            return calculate_travel_time(current, candidate)
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
