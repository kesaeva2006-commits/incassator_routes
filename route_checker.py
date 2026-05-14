"""
Проверка маршрутов на соответствие 8-часовому рабочему дню.
Если маршрут превышает лимит — кластер разбивается на части.

Автор: Анна (Алгоритмист 2)
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
        status = "✅ УКЛАДЫВАЕТСЯ" if is_ok else "❌ ПРЕВЫШЕНИЕ!"
        print(f"\nКластер {i + 1}: {len(route)} банкоматов")
        print(f"  Время в пути: {total_travel_time:.0f} мин")
        print(f"  Общее время: {total_time:.0f} мин / 480 мин")
        print(f"  Статус: {status}")

        if is_ok:
            result["ok"].append(i)
        else:
            result["over_limit"].append(i)
            # Показываем, сколько банкоматов придётся убрать
            trimmed = trim_route_by_time(route,
                                         [calculate_travel_time(route[j], route[j + 1])
                                          for j in range(len(route) - 1)])
            removed = len(route) - len(trimmed)
            print(f"  Чтобы уложиться, нужно убрать {removed} банкоматов с конца маршрута")

    print("\n" + "=" * 60)
    print(f"ИТОГО: {len(result['ok'])} маршрутов укладываются, "
          f"{len(result['over_limit'])} требуют разбиения")
    print("=" * 60 + "\n")

    return result


def split_cluster(cluster: list, max_atms_per_route: int = None) -> list:
    """
    Разбивает кластер на части, если маршрут не укладывается в 8 часов.

    Стратегия: жадное заполнение
    1. Начинаем новый под-кластер
    2. Добавляем банкоматы по одному
    3. Как только время превышает 8 часов — начинаем новый под-кластер

    Параметры:
        cluster — исходный кластер (список банкоматов)
        max_atms_per_route — примерное максимальное количество на маршрут
                              (если не указано, определяется автоматически)

    Возвращает список под-кластеров
    """
    if not cluster:
        return []

    # Если max_atms_per_route не задан, оцениваем его
    if max_atms_per_route is None:
        # Грубая оценка: среднее время на банкомат ~ 20-25 минут
        # 480 минут / 20 минут = 24 банкомата максимум
        # Берём с запасом 20
        max_atms_per_route = 20

    sub_clusters = []
    current_sub = []
    current_time = 30  # начальный резерв

    # Строим временный жадный маршрут для этого кластера
    # (потом Луиза перестроит его нормально)
    remaining = list(cluster)

    while remaining:
        atm = remaining.pop(0)
        current_sub.append(atm)

        # Считаем примерное время для текущего под-кластера
        if len(current_sub) >= 2:
            # Время между предыдущим и текущим
            travel = calculate_travel_time(current_sub[-2], current_sub[-1])
        else:
            travel = 0

        current_time += travel + 15  # 15 минут на обслуживание

        # Если превысили лимит или достигли максимума — завершаем под-кластер
        if current_time > 450 or len(current_sub) >= max_atms_per_route:  # 450 = 480 - запас
            if len(current_sub) > 1:
                # Убираем последний банкомат (он не влез)
                removed = current_sub.pop()
                remaining.insert(0, removed)

            if current_sub:
                sub_clusters.append(current_sub)

            # Начинаем новый под-кластер
            current_sub = []
            current_time = 30

    # Добавляем остаток
    if current_sub:
        sub_clusters.append(current_sub)

    return sub_clusters


def rebuild_routes_for_split_clusters(problem_clusters: list,
                                      routes: list,
                                      check_result: dict) -> list:
    """
    Для кластеров с превышением времени разбивает их и строит новые маршруты.

    Параметры:
        problem_clusters — исходные кластеры (список списков банкоматов)
        routes — исходные маршруты
        check_result — результат проверки (словарь с ключами "ok" и "over_limit")

    Возвращает новый список маршрутов (для всех кластеров)
    """
    new_routes = []
    new_clusters_info = []

    for i, route in enumerate(routes):
        if i in check_result["over_limit"]:
            print(f"\n🔧 Разбиваю кластер {i + 1} ({len(problem_clusters[i])} банкоматов)...")

            # Разбиваем кластер
            sub_clusters = split_cluster(problem_clusters[i])

            print(f"   Получилось {len(sub_clusters)} частей:")
            for j, sub in enumerate(sub_clusters):
                print(f"     Часть {j + 1}: {len(sub)} банкоматов")

            # Строим новый маршрут для каждой части
            for sub in sub_clusters:
                if len(sub) >= 2:
                    new_route = nearest_neighbor_route(sub)
                elif len(sub) == 1:
                    new_route = sub
                else:
                    continue
                new_routes.append(new_route)

            new_clusters_info.append({
                "original_index": i,
                "split_into": len(sub_clusters),
                "parts": [len(s) for s in sub_clusters]
            })
        else:
            # Кластер в порядке, оставляем как есть
            new_routes.append(route)

    print(f"\n📊 После разбиения:")
    print(f"   Было маршрутов: {len(routes)}")
    print(f"   Стало маршрутов: {len(new_routes)}")

    return new_routes


# ============================================================
# ТЕСТОВЫЙ ЗАПУСК (для проверки, что всё работает)
# ============================================================
if __name__ == "__main__":
    from generator import generate_atms
    from clustering import cluster_atms
    from greedy_algorithm import nearest_neighbor_route

    print("Тестирование проверки маршрутов...")

    # Генерируем 1000 банкоматов (или меньше для теста)
    test_atms = generate_atms(100)  # 100 для быстрого теста
    print(f"Сгенерировано банкоматов: {len(test_atms)}")

    # Кластеризуем
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

    # Если есть проблемы — разбиваем
    if check_result["over_limit"]:
        print("Обнаружены проблемные кластеры, выполняю разбиение...")
        new_routes = rebuild_routes_for_split_clusters(clusters, routes, check_result)
    else:
        print("Все маршруты укладываются в 8 часов! 🎉")