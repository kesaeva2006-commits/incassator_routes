import math
WORKDAY_MINUTES = 480  # 8 часов = 480 минут
AVG_SPEED_KMH = 40  # Средняя скорость инкассаторской машины по Москве (грубая оценка)


def calculate_travel_time(atm1, atm2):
    """
    Временный (до Спринта 3) расчет времени между двумя банкоматами.
    Пока используем расстояние по прямой, умноженное на коэффициент извилистости дорог.

    В спринте 3 Алгоритмист 1 заменит это на реальный расчет по OSMnx.
    """
    # Простая формула гаверсинусов для расстояния по координатам
    R = 6371  # Радиус Земли, км

    lat1, lon1 = math.radians(atm1.lat), math.radians(atm1.lon)
    lat2, lon2 = math.radians(atm2.lat), math.radians(atm2.lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance_km = R * c * 1.4  # 1.4 — коэффициент извилистости дорог

    # Время в минутах
    time_minutes = (distance_km / AVG_SPEED_KMH) * 60

    return time_minutes


def check_workday_limit(route_time, service_time_per_atm=15):
    """
    Проверяет, уложится ли маршрут в рабочий день.

    route_time — суммарное время в пути между банкоматами.
    service_time_per_atm — сколько времени инкассатор стоит у каждого банкомата (мин).

    Возвращает (укладывается_ли, общее_время).
    """
    # Количество банкоматов в маршруте
    num_atms = len(route)

    # Общее время = время в пути + время обслуживания всех банкоматов + резерв 30 мин
    total_time = route_time + (num_atms * service_time_per_atm) + 30

    is_ok = total_time <= WORKDAY_MINUTES

    return is_ok, total_time


def trim_route_by_time(route, travel_times):
    """
    Если маршрут не укладывается в 8 часов — обрезает его с конца,
    пока не уложится.
    """
    service_time_per_atm = 15
    accumulated_time = 30  # Резерв в начале дня

    for i, atm in enumerate(route):
        if i > 0:
            accumulated_time += travel_times[i - 1]  # Время доезда до этого банкомата
        accumulated_time += service_time_per_atm

        if accumulated_time > WORKDAY_MINUTES:
            # Этот банкомат уже не влезает, обрезаем маршрут до предыдущего
            return route[:i]

    return route  # Весь маршрут влезает

def print_route_to_console(route, total_minutes):
    """Выводит маршрут в консоль (задачи 32-35)"""
    print("\n" + "=" * 60)
    print("МАРШРУТ ИНКАССАТОРА")
    print("=" * 60)

    for i, atm in enumerate(route, 1):
        print(f"{i}. ATM_{atm.id} | ({atm.lat:.4f}, {atm.lon:.4f})")

    hours = total_minutes // 60
    minutes = total_minutes % 60
    print(f"\nОбщее время: {hours} ч {minutes} мин")

    if total_minutes <= 480:
        print("Успеваем! Маршрут в 8 часов")
    else:
        print("НЕ успеваем! Превышение 8 часов")

    print("=" * 60)