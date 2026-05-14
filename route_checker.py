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
    чтобы каждый маршрут укладывался в 8 часов.

    Алгоритм:
    1. Из перегруженных кластеров убираем "лишние" банкоматы (с конца маршрута)
    2. Добавляем их в кластеры с наименьшей загрузкой
    3. Повторяем, пока все не уложатся или пока не закончатся попытки

    Параметры:
        clusters — исходные 5 кластеров
        routes — исходные 5 маршрутов
        check_result — результат проверки (ok / over_limit)

    Возвращает:
        (новые_кластеры, новые_маршруты)
    """
    max_attempts = 10  # Максимальное количество итераций перераспределения
    attempt = 0

    # Работаем с копиями, чтобы не испортить оригиналы
    new_clusters = [list(c) for c in clusters]

    while check_result["over_limit"] and attempt < max_attempts:
        attempt += 1
        print(f"\nИтерация {attempt}: перераспределение банкоматов...")

        # Находим самый перегруженный кластер (тот, что дал больше всего превышения)
        overloaded_idx = None
        max_overhead = 0

        for idx in check_result["over_limit"]:
            route = routes[idx]
            travel_time = sum(
                calculate_travel_time(route[j], route[j + 1])
                for j in range(len(route) - 1)
            ) if len(route) >= 2 else 0
            _, total_time = check_workday_limit(route, travel_time)
            overhead = total_time - 480

            if overhead > max_overhead:
                max_overhead = overhead
                overloaded_idx = idx

        if overloaded_idx is None:
            break

        # Определяем, сколько банкоматов нужно убрать из перегруженного кластера
        route = routes[overloaded_idx]
        travel_times = [calculate_travel_time(route[j], route[j + 1])
                       for j in range(len(route) - 1)] if len(route) >= 2 else []
        trimmed = trim_route_by_time(route, travel_times)
        excess_atms = route[len(trimmed):]  # Банкоматы, которые не влезли

        if not excess_atms:
            # Если нечего убирать, но всё ещё превышение — убираем последний
            excess_atms = [route[-1]]

        print(f"  Из кластера {overloaded_idx + 1} убрано {len(excess_atms)} банкоматов")

        # Убираем лишние банкоматы из кластера
        for atm in excess_atms:
            if atm in new_clusters[overloaded_idx]:
                new_clusters[overloaded_idx].remove(atm)

        # Распределяем лишние банкоматы по кластерам с наименьшей загрузкой
        for atm in excess_atms:
            # Считаем загрузку всех кластеров (кроме перегруженного)
            loads = []
            for i, cluster in enumerate(new_clusters):
                if i == overloaded_idx:
                    loads.append((i, float('inf')))  # Не добавляем обратно в тот же кластер
                else:
                    # Строим временный маршрут с этим банкоматом
                    temp_cluster = list(cluster) + [atm]
                    if len(temp_cluster) >= 2:
                        temp_route = nearest_neighbor_route(temp_cluster)
                        temp_time = get_route_time(temp_route)
                    else:
                        temp_time = get_route_time(temp_cluster)
                    loads.append((i, temp_time))

            # Находим кластер с минимальной загрузкой, который ещё укладывается в 8 часов
            loads.sort(key=lambda x: x[1])

            placed = False
            for idx, load_time in loads:
                if load_time <= 480:  # Если добавление не нарушает лимит
                    new_clusters[idx].append(atm)
                    print(f"    Банкомат {atm.id} → кластер {idx + 1} (будет {load_time:.0f} мин)")
                    placed = True
                    break

            if not placed:
                # Если никуда не влезает — кладём в наименее загруженный кластер
                best_idx = loads[0][0]
                new_clusters[best_idx].append(atm)
                print(f"    Банкомат {atm.id} → кластер {best_idx + 1} (с превышением, требуется дальнейшая оптимизация)")

        # Перестраиваем все маршруты
        new_routes = []
        for cluster in new_clusters:
            if len(cluster) >= 2:
                new_routes.append(nearest_neighbor_route(cluster))
            elif len(cluster) == 1:
                new_routes.append(cluster)
            else:
                new_routes.append([])

        # Проверяем снова
        check_result = check_all_routes(new_clusters, new_routes)
        routes = new_routes

        # Если после перераспределения всё ещё есть проблемы —
        # в следующей итерации попробуем снова

    print(f"\nПосле {attempt} итераций перераспределения:")
    print(f"   Количество кластеров: {len(new_clusters)}")
    for i, c in enumerate(new_clusters):
        print(f"   Кластер {i + 1}: {len(c)} банкоматов")

    return new_clusters, routes


# ============================================================
# ТЕСТОВЫЙ ЗАПУСК (для проверки, что всё работает)
# ============================================================
if __name__ == "__main__":
    from generator import generate_atms
    from clustering import cluster_atms
    from greedy_algorithm import nearest_neighbor_route

    print("Тестирование проверки маршрутов...")

    # Генерируем банкоматы
    test_atms = generate_atms(100)  # 100 для быстрого теста
    print(f"Сгенерировано банкоматов: {len(test_atms)}")

    # Кластеризуем (строго 5 кластеров — по числу инкассаторов)
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

    # Если есть проблемы — перераспределяем банкоматы
    if check_result["over_limit"]:
        print("Обнаружены проблемные кластеры, перераспределяю банкоматы...")
        new_clusters, new_routes = rebalance_clusters(clusters, routes, check_result)

        print("\n" + "=" * 60)
        print("ФИНАЛЬНАЯ ПРОВЕРКА ПОСЛЕ ПЕРЕРАСПРЕДЕЛЕНИЯ")
        print("=" * 60)
        final_check = check_all_routes(new_clusters, new_routes)

        if final_check["over_limit"]:
            print("\nВнимание: не все маршруты укладываются в 8 часов.")
            print("   Требуется ручная оптимизация или пересмотр количества инкассаторов.")
        else:
            print("\nВсе 5 маршрутов укладываются в 8 часов!")
    else:
        print("Все маршруты укладываются в 8 часов!")