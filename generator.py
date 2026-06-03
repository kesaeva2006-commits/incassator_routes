import random
from atm import Atm


def generate_atms(count: int = 10, seed: int = 42) -> list[Atm]:
    """
    Генерирует список банкоматов.

    :param count: количество банкоматов (10 по умолчанию или 1000 для спринта 2)
    :param seed: фиксирует генератор случайных чисел для повторяемости результатов
    :return: список объектов Atm
    """

    # Фиксируем генератор случайных чисел
    # Это нужно, чтобы при каждом запуске получались одинаковые данные
    if seed is not None:
        random.seed(seed)

    atms = []  # список, в который будем добавлять все банкоматы

    # Границы Москвы (примерная область генерации координат)
    # Используется, чтобы банкоматы были в реалистичной географии
    LAT_MIN, LAT_MAX = 55.55, 55.95  # широта (север-юг)
    LON_MIN, LON_MAX = 37.30, 37.95  # долгота (запад-восток)

    # Генерация нужного количества банкоматов
    for i in range(1, count + 1):

        # Генерируем случайные координаты внутри Москвы
        lat = round(random.uniform(LAT_MIN, LAT_MAX), 6)
        lon = round(random.uniform(LON_MIN, LON_MAX), 6)

        # Генерируем параметры вместимости банкомата
        # (разные размеры: от маленьких до крупных)
        cap_in = random.randint(8000, 30000)   # приём денег
        cap_out = random.randint(10000, 25000)  # выдача денег

        mean_in = random.uniform(80, 200)
        std_in = random.uniform(8, 30)
        mean_out = random.uniform(70,110)
        std_out = random.uniform(8, 25)

        # Создаём объект банкомата
        atm = Atm(
            atm_id=i,               # уникальный ID
            lat=lat,                # широта
            lon=lon,                # долгота
            capacity_in=cap_in,     # максимум приёма
            capacity_out=cap_out,   # максимум выдачи

            mean_in=mean_in, # статистика внесений
            std_in=std_in,
            mean_out=mean_out, # статистика снятий
            std_out=std_out
        )
            
        # Добавляем банкомат в список
        atms.append(atm)

    # Возвращаем готовый список банкоматов
    return atms
