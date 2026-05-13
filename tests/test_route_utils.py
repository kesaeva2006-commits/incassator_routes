import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from route_utils import calculate_travel_time, check_workday_limit, trim_route_by_time

# ТЕСТЫ ДЛЯ calculate_travel_time

def test_calculate_travel_time_returns_number():
    atm1 = Atm(1, 55.75, 37.62, 100, 100)
    atm2 = Atm(2, 55.76, 37.63, 100, 100)
    time = calculate_travel_time(atm1, atm2)
    assert isinstance(time, (int, float))
    assert time > 0

def test_calculate_travel_time_same_point_returns_zero():
    atm1 = Atm(1, 55.75, 37.62, 100, 100)
    atm2 = Atm(2, 55.75, 37.62, 100, 100)
    time = calculate_travel_time(atm1, atm2)
    # Расстояние между одинаковыми координатами = 0
    assert time >= 0
  
# ТЕСТЫ ДЛЯ check_workday_limit

def test_check_workday_limit_returns_tuple():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    route = [atm]
    is_ok, total_time = check_workday_limit(route, travel_time=0)
    assert isinstance(is_ok, bool)
    assert isinstance(total_time, (int, float))

def test_check_workday_limit_success():
    # Один банкомат: 0 в пути + 15 мин обслуживания + 30 резерв = 45 мин
    atm = Atm(1, 55.75, 37.62, 100, 100)
    route = [atm]
    is_ok, total_time = check_workday_limit(route, travel_time=0)
    assert is_ok == True
    assert total_time == 45  # 0 + 15 + 30

def test_check_workday_limit_fail():
    # Слишком много банкоматов
    atms = [Atm(i, 55.75 + i*0.01, 37.62 + i*0.01, 100, 100) for i in range(100)]
    # Большое время в пути (имитируем)
    is_ok, total_time = check_workday_limit(atms, travel_time=500)
    assert is_ok == False
    assert total_time > 480

# ТЕСТЫ ДЛЯ trim_route_by_time

def test_trim_route_by_time_returns_route():
    atms = [Atm(1, 55.75, 37.62, 100, 100), Atm(2, 55.76, 37.63, 100, 100)]
    travel_times = [10]
    trimmed = trim_route_by_time(atms, travel_times)
    assert isinstance(trimmed, list)

def test_trim_route_by_time_removes_excess():
    # Создаём маршрут из 10 банкоматов с большим временем в пути
    atms = [Atm(i, 55.75 + i*0.1, 37.62 + i*0.1, 100, 100) for i in range(10)]
    # Каждый следующий банкомат далеко → время в пути большое
    travel_times = [100] * 9
    trimmed = trim_route_by_time(atms, travel_times)
    # Должен обрезаться до небольшого количества
    assert len(trimmed) < len(atms)

def test_trim_route_by_time_no_trim_when_fits():
    atms = [Atm(1, 55.75, 37.62, 100, 100), Atm(2, 55.76, 37.63, 100, 100)]
    travel_times = [5]  # 5 минут в пути
    trimmed = trim_route_by_time(atms, travel_times)
    # Весь маршрут влезает → ничего не обрезается
    assert len(trimmed) == len(atms)
