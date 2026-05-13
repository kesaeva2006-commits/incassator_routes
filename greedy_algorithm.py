import math
from atm import Atm


def distance(a: Atm, b: Atm) -> float:
    """
    Вычисляет расстояние между двумя банкоматами по координатам.
    Используется евклидово расстояние .
    """
    return math.sqrt((a.lat - b.lat) ** 2 + (a.lon - b.lon) ** 2)


def nearest_neighbor_route(atms: list[Atm], start_atm: Atm | None = None) -> list[Atm]:
    """
    Строит маршрут обхода банкоматов с помощью жадного алгоритма
    (метод ближайшего соседа)

    :param atms: список банкоматов
    :param start_atm: начальный банкомат (если не задан — берём первый)
    :return: список банкоматов в порядке обхода
    """

    # Если список пустой — возвращаем пустой маршрут
    if not atms:
        return []

    # Копируем список, чтобы не изменять исходный
    unvisited = atms.copy()

    # Определяем начальную точку маршрута
    if start_atm:
        current = start_atm
        unvisited.remove(start_atm)  # удаляем его из непосещённых
    else:
        current = unvisited.pop(0)   # берём первый банкомат

    # Начинаем маршрут с текущего банкомата
    route = [current]

    # Пока есть непосещённые банкоматы
    while unvisited:
        # Находим ближайший банкомат к текущему
        nearest = min(
            unvisited,
            key=lambda atm: distance(current, atm)
        )

        # Добавляем его в маршрут
        route.append(nearest)

        # Удаляем из списка непосещённых
        unvisited.remove(nearest)

        # Переходим к нему (он становится текущим)
        current = nearest

    # Возвращаем готовый маршрут
    return route
