import random
from atm import Atm


def generate_large_atm_network(count: int = 1000, seed: int = 2026) -> list[Atm]:
    """
    Генерирует сеть банкоматов по всей территории Москвы.

    :param count: количество банкоматов (по умолчанию 1000)
    :param seed: фиксированный seed для воспроизводимости результатов
                 (если None — каждый запуск будет давать разные данные)
    :return: список объектов Atm
    """

    # Устанавливаем seed ТОЛЬКО если он задан
    # Это позволяет управлять воспроизводимостью:
    # seed=2026 → одинаковые данные
    # seed=None → каждый раз новые банкоматы
    if seed is not None:
        random.seed(seed)

    atms = []  # список для хранения всех банкоматов

    # Границы Москвы (примерный bounding box)
    LAT_MIN, LAT_MAX = 55.55, 55.95  # Юг — Север
    LON_MIN, LON_MAX = 37.30, 37.95  # Запад — Восток

    # Генерируем нужное количество банкоматов
    for i in range(1, count + 1):

        # Случайные координаты в пределах Москвы
        lat = round(random.uniform(LAT_MIN, LAT_MAX), 6)
        lon = round(random.uniform(LON_MIN, LON_MAX), 6)

        # Случайная вместимость бункеров
        # имитируем разные типы банкоматов (маленькие/большие)
        cap_in = random.randint(8000, 30000)
        cap_out = random.randint(10000, 25000)

        # Создаём объект банкомата
        atm = Atm(
            atm_id=i,
            lat=lat,
            lon=lon,
            capacity_in=cap_in,
            capacity_out=cap_out,

            # Пока статистика не используется (для спринта 3)
            mean_in=0,
            std_in=0,
            mean_out=0,
            std_out=0
        )

        # Добавляем в список
        atms.append(atm)

    # Возвращаем список банкоматов
    return atms
