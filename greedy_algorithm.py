import networkx as nx
from atm import Atm
from map_loader import load_moscow_graph
from node_matcher import match_atms_to_nodes


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


def nearest_neighbor_route(atms: list[Atm], start_atm: Atm | None = None) -> list[Atm]:
    """
    Строит маршрут обхода банкоматов с помощью жадного алгоритма
    (метод ближайшего соседа).

    В отличие от базовой версии:
    используется реальное время движения по дорогам,
    а не расстояние по прямой.

    :param atms: список банкоматов
    :param start_atm: начальный банкомат (если не задан — берётся первый)
    :return: список банкоматов в порядке обхода
    """

    # Если список пустой — возвращаем пустой маршрут
    if not atms:
        return []

    # Загружаем граф дорог Москвы (из кэша или скачиваем)
    G = load_moscow_graph()

    # Привязываем каждый банкомат к ближайшему узлу графа (перекрёстку)
    # Это делается один раз для ускорения работы алгоритма
    atm_to_node = match_atms_to_nodes(atms)

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

        # Выбираем банкомат с минимальным временем поездки
        # от текущего (жадный выбор)
        nearest = min(
            unvisited,
            key=lambda atm: travel_time_between(current, atm, G, atm_to_node)
        )

        # Добавляем его в маршрут
        route.append(nearest)

        # Удаляем из списка непосещённых
        unvisited.remove(nearest)

        # Переходим к нему — он становится текущим
        current = nearest

    # Возвращаем готовый маршрут
    return route
