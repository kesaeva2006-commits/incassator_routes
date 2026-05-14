"""
Проверка маршрутов на соответствие 8-часовому рабочему дню.
Если маршрут превышает лимит — банкоматы перераспределяются между 5 кластерами.

"""

from route_utils import check_workday_limit, trim_route_by_time, calculate_travel_time
from greedy_algorithm import nearest_neighbor_route


def check_all_routes(clusters: list, routes: list) -> dict:
    """
    Проверяет все маршруты на соответствие 8-часовому лимиту.

    Параметры:
        clusters — список кластеров (каждый кластер = список банкоматов)
        routes — список маршрутов (каждый маршрут = список банкоматов по порядку)

    Возвращает словарь:
    {
        "ok": [0, 2],           # индексы кластеров, которые укладываются
        "over_limit": [1, 3, 4] # индексы кластеров, которые НЕ укладываются
    }
    """
    result = {
        "ok": [],
        "over_limit": []
    }

    print("\n" + "=" * 60)
    print("ПРОВЕРКА МАРШРУТОВ НА 8 ЧАСОВ (480 минут)")
    print("=" * 60)

    for i, route in enumerate(routes):
        # Считаем общее время в пути для этого маршрута
        total_travel_time = 0
        for j in range(len(route) - 1):
            total_travel_time += calculate_travel_time(route[j], route[j + 1])

        # Проверяем, укладывается ли маршрут в рабочий день
        is_ok, total_time = check_workday_limit(route, total_travel_time)

        # Красивый вывод в консоль
        status = "УКЛАДЫВАЕТСЯ" if is_ok else "ПРЕВЫШЕНИЕ!"
        print(f"\nКластер {i + 1}: {len(route)} банкоматов")
        print(f"  Время в пути: {total_travel_time:.0f} мин")
        print(f"  Общее время: {total_time:.0f} мин / 480 мин")
        print(f"  Статус: {status}")

        if is_ok:
            result["ok"].append(i)
        else:
            result["over_limit"].append(i)
            # Показываем, сколько банкоматов нужно убрать
            trimmed = trim_route_by_time(route,
                                         [calculate_travel_time(route[j], route[j + 1])
                                          for j in range(len(route) - 1)])
            removed = len(route) - len(trimmed)
            print(f"  Нужно убрать {removed} банкоматов, чтобы уложиться в 8 часов")

    print("\n" + "=" * 60)
    print(f"ИТОГО: {len(result['ok'])} маршрутов укладываются, "
          f"{len(result['over_limit'])} требуют корректировки")
    print("=" * 60 + "\n")

    return result


def get_route_time(route: list) -> float:
    """
    Считает общее время маршрута (в пути + обслуживание + резерв).
    Нужно для сравнения загруженности кластеров.
    """
    if len(route) < 2:
        return 30 + len(route) * 15  # только резерв и обслуживание

    travel_time = sum(
        calculate_travel_time(route[i], route[i + 1])
        for i in range(len(route) - 1)
    )
    _, total_time = check_workday_limit(route, travel_time)
    return total_time


def rebalance_clusters(clusters: list, routes: list, check_result: dict) -> tuple:
    """
    Перераспределяет банкоматы между 5 кластерами так,
    чтобы каждый маршрут гарантированно укладывался в 8 часов.

    Алгоритм:
    1. Для каждого перегруженного кластера обрезаем маршрут до 480 минут
    2. "Лишние" банкоматы собираем в общий пул
    3. Пул распределяем по кластерам, у которых есть запас по времени
    4. Если банкомат не влезает никуда — он остаётся в очереди на следующий день

    Параметры:
        clusters — исходные 5 кластеров
        routes — исходные 5 маршрутов
        check_result — результат проверки (ok / over_limit)

    Возвращает:
        (новые_кластеры, новые_маршруты, очередь_на_завтра)
    """
    # Работаем с копиями
    new_clusters = [list(c) for c in clusters]
    overflow_queue = []  # Банкоматы, которые не влезли ни в один кластер

    print("\n ПЕРЕРАСПРЕДЕЛЕНИЕ БАНКОМАТОВ")
    print("=" * 60)

    # Шаг 1: Обрезаем все перегруженные маршруты до 480 минут
    for idx in check_result["over_limit"]:
        route = routes[idx]

        # Считаем время для каждого отрезка маршрута
        travel_times = []
        for j in range(len(route) - 1):
            travel_times.append(calculate_travel_time(route[j], route[j + 1]))

        # Обрезаем маршрут
        trimmed_route = trim_route_by_time(route, travel_times)

        # Банкоматы, которые не влезли
        excess = route[len(trimmed_route):]

        if excess:
            print(f"\nКластер {idx + 1}: убрано {len(excess)} банкоматов")
            for atm in excess:
                print(f"  • Банкомат {atm.id} (lat={atm.lat:.3f}, lon={atm.lon:.3f})")
                # Удаляем из кластера
                if atm in new_clusters[idx]:
                    new_clusters[idx].remove(atm)
                # Добавляем в очередь на перераспределение
                overflow_queue.append(atm)

    print(f"\n Очередь на перераспределение: {len(overflow_queue)} банкоматов")

    # Шаг 2: Пытаемся распределить очередь по кластерам с запасом
    # Сортируем кластеры по загруженности (от наименее загруженных к наиболее)

    not_placed = []  # Банкоматы, которые не удалось разместить

    for atm in overflow_queue:
        # Считаем текущую загрузку всех кластеров с учётом этого банкомата
        cluster_loads = []

        for i, cluster in enumerate(new_clusters):
            # Временный кластер с новым банкоматом
            temp_cluster = list(cluster) + [atm]

            if len(temp_cluster) >= 2:
                temp_route = nearest_neighbor_route(temp_cluster)
                temp_time = get_route_time(temp_route)
            else:
                temp_time = get_route_time(temp_cluster)

            cluster_loads.append((i, temp_time, len(temp_cluster)))

        # Сортируем: сначала те, куда банкомат влезает (≤480 мин),
        # потом по возрастанию загрузки
        cluster_loads.sort(key=lambda x: (0 if x[1] <= 480 else 1, x[1]))

        placed = False
        for idx, load_time, _ in cluster_loads:
            if load_time <= 480:
                # Влезает! Добавляем в этот кластер
                new_clusters[idx].append(atm)
                print(
                    f"   Банкомат {atm.id} → кластер {idx + 1} (стало {len(new_clusters[idx])} банкоматов, {load_time:.0f} мин)")
                placed = True
                break

        if not placed:
            # Не влез никуда — в очередь на следующий день
            not_placed.append(atm)
            print(f"   Банкомат {atm.id} → не влезает ни в один кластер, перенесён на следующий день")

    # Шаг 3: Перестраиваем все маршруты
    new_routes = []
    for cluster in new_clusters:
        if len(cluster) >= 2:
            new_routes.append(nearest_neighbor_route(cluster))
        elif len(cluster) == 1:
            new_routes.append(cluster)
        else:
            new_routes.append([])

    # Финальная проверка
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ПЕРЕРАСПРЕДЕЛЕНИЯ")
    print("=" * 60)

    final_check = check_all_routes(new_clusters, new_routes)

    if final_check["over_limit"]:
        print("\n Всё ещё есть проблемы. Пробую принудительно обрезать...")
        # Принудительно обрезаем оставшиеся проблемные маршруты
        for idx in final_check["over_limit"]:
            route = new_routes[idx]
            travel_times = [calculate_travel_time(route[j], route[j + 1])
                            for j in range(len(route) - 1)] if len(route) >= 2 else []
            trimmed = trim_route_by_time(route, travel_times)

            if len(trimmed) < len(route):
                removed = route[len(trimmed):]
                for atm in removed:
                    if atm in new_clusters[idx]:
                        new_clusters[idx].remove(atm)
                    not_placed.append(atm)

                # Перестраиваем маршрут
                if len(new_clusters[idx]) >= 2:
                    new_routes[idx] = nearest_neighbor_route(new_clusters[idx])
                elif len(new_clusters[idx]) == 1:
                    new_routes[idx] = new_clusters[idx]
                else:
                    new_routes[idx] = []

        # Финальная-финальная проверка
        print("\n" + "=" * 60)
        print("ФИНАЛЬНАЯ ПРОВЕРКА (ПОСЛЕ ПРИНУДИТЕЛЬНОГО ОБРЕЗАНИЯ)")
        print("=" * 60)
        check_all_routes(new_clusters, new_routes)

    print(f"\nИТОГО:")
    print(f"   Кластеров: {len(new_clusters)}")
    for i, c in enumerate(new_clusters):
        print(f"   Кластер {i + 1}: {len(c)} банкоматов")
    print(f"   Перенесено на следующий день: {len(not_placed)} банкоматов")
    if not_placed:
        print(f"   ID необслуженных банкоматов: {[atm.id for atm in not_placed]}")

    return new_clusters, new_routes, not_placed


# ============================================================
# ТЕСТОВЫЙ ЗАПУСК (для проверки, что всё работает)
# ============================================================
if __name__ == "__main__":
    from generator import generate_atms
    from clustering import cluster_atms
    from greedy_algorithm import nearest_neighbor_route

    print("Тестирование проверки маршрутов...")

    # Генерируем банкоматы
    test_atms = generate_atms(100)
    print(f"Сгенерировано банкоматов: {len(test_atms)}")

    # Кластеризуем (строго 5 кластеров)
    clusters = cluster_atms(test_atms, n_clusters=5)
    print(f"Кластеров: {len(clusters)}")
    for i, c in enumerate(clusters):
        print(f"  Кластер {i + 1}: {len(c)} банкоматов")

    # Строим маршруты
    routes = []
    for cluster in clusters:
        if len(cluster) >= 2:
            route = nearest_neighbor_route(cluster)
        elif len(cluster) == 1:
            route = cluster
        else:
            route = []
        routes.append(route)

    # Проверяем
    check_result = check_all_routes(clusters, routes)

    # Если есть проблемы — перераспределяем
    if check_result["over_limit"]:
        print("\nОбнаружены проблемные кластеры, перераспределяю банкоматы...")
        new_clusters, new_routes, next_day_queue = rebalance_clusters(
            clusters, routes, check_result
        )

        if next_day_queue:
            print(f"\n {len(next_day_queue)} банкоматов перенесены на следующий день.")
            print("   Это нормально: необязательно каждый день объезжать все банкоматы (п.5 ТЗ)")
    else:
        print("\nВсе маршруты укладываются в 8 часов!")