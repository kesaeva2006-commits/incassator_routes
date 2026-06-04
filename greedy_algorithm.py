import networkx as nx
from atm import Atm
from route_utils import calculate_travel_time
from map_loader import load_moscow_graph
from node_matcher import match_atms_to_nodes


def travel_time_between(a: Atm, b: Atm, G, atm_to_node: dict) -> float:
    """
    Считает реальное время в пути между двумя банкоматами по дорожному графу.
    """
    node_a = atm_to_node[a.id]
    node_b = atm_to_node[b.id]
    try:
        return nx.shortest_path_length(G, node_a, node_b, weight='travel_time')
    except nx.NetworkXNoPath:
        return float('inf')  # путь не найден — банкомат недостижим,
                             # бесконечность гарантирует что он не будет выбран алгоритмом


def build_time_matrix(atms, G, atm_to_node):
    """
    Строит матрицу времён между всеми парами банкоматов.
    Один запуск Дейкстры на каждый банкомат находит время до ВСЕХ остальных.
    :param atms: список банкоматов
    :param G: граф дорог
    :param atm_to_node: привязка банкоматов к узлам графа
    :return: словарь {(id_a, id_b): время_в_секундах}
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
        nearest = min(unvisited, key=lambda atm: matrix[(current.id, atm.id)])  # переименовано a -> atm
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    return route


def nearest_neighbor_route(atms: list[Atm], start_atm=None,
                           use_graph: bool = True, G=None, atm_to_node=None) -> list[Atm]:
    """
    Строит маршрут обхода банкоматов методом ближайшего соседа.
    :param atms: список банкоматов
    :param start_atm: начальный банкомат (если None — берётся первый из списка)
    :param use_graph: True — использовать граф дорог, False — прямое расстояние
    :param G: граф дорог (если None — загружается автоматически)
    :param atm_to_node: привязка банкоматов к узлам графа
    :return: список банкоматов в порядке обхода
    """
    if not atms:
        return []
    if use_graph:
        if G is None:
            G = load_moscow_graph()
        if atm_to_node is None:
            atm_to_node = match_atms_to_nodes(atms, G)
        return nearest_neighbor_route_matrix(atms, G, atm_to_node)
    else:
        unvisited = atms.copy()
        if start_atm:
            if start_atm not in atms:  # явная проверка с информативным сообщением
                raise ValueError(
                    f"start_atm (id={start_atm.id}) отсутствует в списке atms"
                )
            current = start_atm
            unvisited.remove(start_atm)
        else:
            current = unvisited.pop(0)
        route = [current]
        while unvisited:
            nearest = min(unvisited, key=lambda atm: calculate_travel_time(current, atm))  # убрана лишняя time_to
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        return route
