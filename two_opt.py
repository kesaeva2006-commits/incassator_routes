from atm import Atm
from map_loader import load_moscow_graph
from node_matcher import match_atms_to_nodes
from greedy_algorithm import travel_time_between


def route_total_time(route: list[Atm], G, atm_to_node: dict) -> float:
    """
    Считает суммарное время маршрута в секундах.

    :param route: список банкоматов в порядке обхода
    :param G: граф дорог
    :param atm_to_node: привязка банкоматов к перекрёсткам
    :return: общее время маршрута в секундах
    """

    total = 0.0  # здесь будем накапливать общее время маршрута

    # Проходим по всем парам соседних банкоматов
    # например: (1→2), (2→3), (3→4)
    for i in range(len(route) - 1):

        # считаем время между текущим и следующим банкоматом
        # и прибавляем к общей сумме
        total += travel_time_between(route[i], route[i + 1], G, atm_to_node)

    return total  # возвращаем итоговое время


def two_opt(route: list[Atm]) -> list[Atm]:
    """
    Улучшает маршрут алгоритмом 2-opt.

    Идея:
    Жадный алгоритм даёт быстрый, но не всегда оптимальный маршрут.
    Часто в нём есть "перекрёсты" (лишние петли).
    2-opt устраняет их, разворачивая куски маршрута.

    :param route: маршрут от жадного алгоритма
    :return: улучшенный маршрут
    """

    # Если банкоматов слишком мало — оптимизация не имеет смысла
    if len(route) < 4:
        return route

    # Загружаем граф дорог (один раз!)
    G = load_moscow_graph()

    # Привязываем каждый банкомат к ближайшему узлу графа
    atm_to_node = match_atms_to_nodes(route)

    # Копируем исходный маршрут (чтобы не портить его)
    best_route = route.copy()

    # Считаем время текущего маршрута
    best_time = route_total_time(best_route, G, atm_to_node)

    improved = True  # флаг: было ли улучшение

    # Повторяем, пока можем улучшать маршрут
    while improved:
        improved = False  # считаем, что улучшений нет

        # Перебираем все возможные пары индексов i и j
        for i in range(1, len(best_route) - 2):
            for j in range(i + 1, len(best_route)):

                # Создаём новый маршрут:
                # берём кусок между i и j и разворачиваем его
                new_route = (
                    best_route[:i] +                  # начало без изменений
                    best_route[i:j + 1][::-1] +      # перевёрнутый участок
                    best_route[j + 1:]               # конец без изменений
                )

                # Считаем время нового маршрута
                new_time = route_total_time(new_route, G, atm_to_node)

                # Если стало лучше (быстрее) — сохраняем
                if new_time < best_time:
                    best_route = new_route
                    best_time = new_time
                    improved = True  # нашли улучшение — продолжаем цикл

    return best_route  # возвращаем лучший найденный маршрут
