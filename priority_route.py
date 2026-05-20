"""
Приоритетный объезд банкоматов: сначала RED, потом YELLOW, потом GREEN.
"""

from atm import Atm
from greedy_algorithm import nearest_neighbor_route


def sort_by_priority(atms: list) -> list:
    """
    Сортирует банкоматы по уровню риска: RED → YELLOW → GREEN.
    Внутри каждой группы сохраняется исходный порядок.

    :param atms: список банкоматов
    :return: отсортированный список
    """
    priority_order = {"RED": 0, "YELLOW": 1, "GREEN": 2}

    return sorted(atms, key=lambda atm: priority_order.get(atm.get_risk_level(), 2))


def build_priority_route(atms: list) -> list:
    """
    Строит маршрут с приоритетом: сначала критические банкоматы.

    1. Сортируем банкоматы по риску (RED → YELLOW → GREEN)
    2. Строим жадный маршрут

    :param atms: список банкоматов
    :return: упорядоченный маршрут
    """
    if len(atms) < 2:
        return atms

    # Сортируем по приоритету
    sorted_atms = sort_by_priority(atms)

    # Строим маршрут
    route = nearest_neighbor_route(sorted_atms)

    return route


def print_priority_summary(atms: list):
    """
    Выводит сводку по приоритетам банкоматов.

    :param atms: список банкоматов
    """
    red = [atm for atm in atms if atm.get_risk_level() == "RED"]
    yellow = [atm for atm in atms if atm.get_risk_level() == "YELLOW"]
    green = [atm for atm in atms if atm.get_risk_level() == "GREEN"]

    print(f"\nПРИОРИТЕТЫ БАНКОМАТОВ:")
    print(f"   RED:    {len(red)} банкоматов")
    if red:
        for atm in red:
            print(
                f"      • Банкомат {atm.id}: in={atm.current_in}/{atm.capacity_in}, out={atm.current_out}/{atm.capacity_out}")

    print(f"   YELLOW: {len(yellow)} банкоматов")
    if yellow:
        for atm in yellow:
            print(
                f"      • Банкомат {atm.id}: in={atm.current_in}/{atm.capacity_in}, out={atm.current_out}/{atm.capacity_out}")

    print(f"   GREEN:  {len(green)} банкоматов")