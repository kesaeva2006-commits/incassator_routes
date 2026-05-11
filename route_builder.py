from greedy_algorithm import nearest_neighbor_route
from atm import Atm

def build_routes_for_clusters(clusters: list[list[Atm]]) -> list[list[Atm]]:
    """
    Строит жадные маршруты для каждого кластера.
    На вход подаются кластеры (результат KMeans),
    на выходе — маршруты обхода банкоматов внутри каждого кластера.
    """

    # Список для хранения итоговых маршрутов
    all_routes = []

    # Проходим по каждому кластеру (каждая группа банкоматов)
    for cluster_atms in clusters:

        # Если кластер пустой — добавляем пустой маршрут
        # (на случай, если KMeans дал пустую группу)
        if not cluster_atms:
            all_routes.append([])
            continue

        # Строим маршрут внутри текущего кластера
        # жадный алгоритм выбирает ближайший следующий банкомат
        route = nearest_neighbor_route(cluster_atms, start_atm=None)

        # Добавляем полученный маршрут в общий список
        all_routes.append(route)

    # Возвращаем список всех маршрутов (по одному на кластер)
    return all_routes
