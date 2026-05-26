"""
Построение маршрутов на 3 дня с пересчётом прогноза заполненности бункеров.

ПСЕВДОКОД АЛГОРИТМА:
1. Копируем список банкоматов (чтобы не испортить оригинал)
2. Устанавливаем начальные уровни: current_in = 0, current_out = capacity_out
3. Для каждого дня (1, 2, 3):
    а. Вывести приоритеты банкоматов (RED / YELLOW / GREEN)
    б. Отсортировать банкоматы по приоритету (RED → YELLOW → GREEN)
    в. Разбить на 5 кластеров (cluster_atms)
    г. Для каждого кластера построить маршрут (build_priority_route)
    д. Проверить, что маршруты укладываются в 8 часов (check_all_routes)
    е. Если нет — перераспределить банкоматы (rebalance_clusters)
    ж. Сохранить результат в план
    з. Если это не последний день:
        - Обновить уровни бункеров (update_levels, 24 часа)
        - Добавить необслуженные банкоматы в очередь на завтра
4. Вернуть план (словарь по дням)

ВАЖНО: Банкоматы, не влезающие в расписание, переносятся на следующий день.
Это соответствует требованию ТЗ: «необязательно каждый день объезжать все банкоматы».
"""

from atm import Atm
from greedy_algorithm import nearest_neighbor_route
from route_checker import check_all_routes, rebalance_clusters, get_route_time
from priority_route import build_priority_route, print_priority_summary


def plan_multi_day(all_atms: list, days: int = 3, hours_per_day: int = 24) -> dict:
    """
    Строит маршруты на несколько дней с пересчётом прогноза после каждого дня.

    Алгоритм:
    1. День 1: определить приоритеты, построить маршруты
    2. После дня: обновить уровни бункеров (прошло 24 часа)
    3. День 2: пересчитать приоритеты, построить маршруты
    4. И так далее...

    :param all_atms: все банкоматы
    :param days: на сколько дней строим план
    :param hours_per_day: сколько часов проходит между днями
    :return: словарь {день: {"routes": [...], "queue": [...], "summary": {...}}}
    """
    from clustering import cluster_atms

    plan = {}

    # Работаем с копией списка банкоматов
    current_atms = [Atm(
        atm_id=atm.id,
        lat=atm.lat,
        lon=atm.lon,
        capacity_in=atm.capacity_in,
        capacity_out=atm.capacity_out,
        mean_in=atm.mean_in,
        std_in=atm.std_in,
        mean_out=atm.mean_out,
        std_out=atm.std_out
    ) for atm in all_atms]

    # Устанавливаем начальные уровни
    for atm in current_atms:
        atm.current_in = 0
        atm.current_out = atm.capacity_out

    for day in range(1, days + 1):
        print(f"\n{'=' * 60}")
        print(f"📅 ДЕНЬ {day}")
        print(f"{'=' * 60}")

        # Показываем приоритеты на начало дня
        print_priority_summary(current_atms)

        # Сортируем банкоматы по приоритету
        priority_order = {"RED": 0, "YELLOW": 1, "GREEN": 2}
        current_atms.sort(key=lambda atm: priority_order.get(atm.get_risk_level(), 2))

        # Кластеризуем
        clusters = cluster_atms(current_atms, n_clusters=5)

        # Строим маршруты
        routes = []
        for cluster in clusters:
            if len(cluster) >= 2:
                route = build_priority_route(cluster)
            elif len(cluster) == 1:
                route = cluster
            else:
                route = []
            routes.append(route)

        # Проверяем и корректируем
        check_result = check_all_routes(clusters, routes)

        if check_result["over_limit"]:
            print(f"\nОбнаружены проблемные маршруты, перераспределяю...")
            new_clusters, new_routes, queue = rebalance_clusters(clusters, routes, check_result)

            plan[day] = {
                "routes": new_routes,
                "clusters": new_clusters,
                "queue": queue
            }
        else:
            print(f"\n Все маршруты укладываются в 8 часов!")
            plan[day] = {
                "routes": routes,
                "clusters": clusters,
                "queue": []
            }

        # Сводка дня
        total_serviced = sum(len(c) for c in plan[day]["clusters"])
        total_queued = len(plan[day]["queue"])

        print(f"\nИтоги дня {day}:")
        print(f"   Обслужено: {total_serviced} банкоматов")
        print(f"   Перенесено на завтра: {total_queued} банкоматов")

        # Обновляем уровни бункеров для следующего дня
        if day < days:
            print(f"\nПрошло {hours_per_day} часов. Обновляю уровни бункеров...")
            for atm in current_atms:
                atm.update_levels(hours_per_day)

            # Добавляем необслуженные банкоматы в список на следующий день
            if plan[day]["queue"]:
                current_atms = plan[day]["queue"] + [
                    atm for atm in current_atms
                    if atm not in plan[day]["queue"]
                ]

    return plan


# ============================================================
# ТЕСТОВЫЙ ЗАПУСК
# ============================================================
if __name__ == "__main__":
    from generator import generate_atms

    print("Тестирование многодневного планирования...")

    # Генерируем банкоматы
    test_atms = generate_atms(100)
    print(f"Сгенерировано банкоматов: {len(test_atms)}")

    # Планируем на 3 дня
    plan = plan_multi_day(test_atms, days=3)

    print(f"\n{'=' * 60}")
    print("ИТОГОВЫЙ ПЛАН НА 3 ДНЯ")
    print(f"{'=' * 60}")

    for day, data in plan.items():
        routes = data["routes"]
        queue = data["queue"]
        total = sum(len(r) for r in routes)
        print(f"День {day}: {total} банкоматов обслужено, {len(queue)} перенесено")