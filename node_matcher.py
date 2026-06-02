import osmnx as ox
from atm import Atm
from map_loader import load_moscow_graph


def match_atms_to_nodes(atms: list[Atm], G=None) -> dict[int, int]:
    """
    Для каждого банкомата находит ближайший узел (перекрёсток) на карте дорог.

    Зачем это нужно:
    Банкомат стоит в здании — он не на дороге.
    Чтобы строить маршрут по дорогам, нужно привязать
    каждый банкомат к ближайшему перекрёстку на карте.

    :param atms: список банкоматов
    :param G: граф дорог — если передан снаружи, не загружает повторно
    :return: словарь {atm_id: node_id}
             atm_id  — ID банкомата
             node_id — ID ближайшего перекрёстка в графе
    """

    # Загружаем граф только если не передали снаружи
    if G is None:
        G = load_moscow_graph()

    # Собираем координаты всех банкоматов в два списка
    lats = [atm.lat for atm in atms]  # широты
    lons = [atm.lon for atm in atms]  # долготы

    # Находим ближайший перекрёсток для каждого банкомата сразу
    # lons идут первыми (X), потом lats (Y) — так требует osmnx
    nearest_nodes = ox.nearest_nodes(G, lons, lats)

    # Собираем результат в словарь {atm_id: node_id}
    atm_to_node = {}
    for atm, node_id in zip(atms, nearest_nodes):
        atm_to_node[atm.id] = node_id

    return atm_to_node
