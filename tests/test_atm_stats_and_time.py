import sys
import os
import pytest

if not os.path.exists('atm.py'):
    pytest.skip("atm.py ещё нет в main", allow_module_level=True)
# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from route_utils import calculate_travel_time, check_workday_limit

# Тест 1: проверяет, что метод predict_level_after_hours возвращает числа
def test_predict_returns_floats():
    atm = Atm(1, 55.75, 37.62, 100, 100, 10, 2, 15, 3)
    pred_in, pred_out = atm.predict_level_after_hours(24)
    assert isinstance(pred_in, (int, float))
    assert isinstance(pred_out, (int, float))

# Тест 2: проверяет, что метод is_critical возвращает (bool, str)
def test_is_critical_returns_tuple():
    atm = Atm(1, 55.75, 37.62, 100, 100, 10, 2, 15, 3)
    is_crit, reason = atm.is_critical(24)
    assert isinstance(is_crit, bool)
    assert isinstance(reason, str)

# Тест 3: проверяет, что calculate_travel_time возвращает положительное число
def test_travel_time_positive():
    atm1 = Atm(1, 55.75, 37.62, 100, 100, 10, 2, 15, 3)
    atm2 = Atm(2, 55.76, 37.63, 100, 100, 10, 2, 15, 3)
    time = calculate_travel_time(atm1, atm2)
    assert isinstance(time, (int, float))
    assert time > 0

# Тест 4: проверяет, что check_workday_limit возвращает кортеж (bool, число)
def test_workday_limit_returns_tuple():
    atm1 = Atm(1, 55.75, 37.62, 100, 100, 10, 2, 15, 3)
    atm2 = Atm(2, 55.76, 37.63, 100, 100, 10, 2, 15, 3)
    route = [atm1, atm2]
    travel_times = [calculate_travel_time(route[0], route[1])]
    is_ok, total_time = check_workday_limit(route, travel_times)
    assert isinstance(is_ok, bool)
    assert isinstance(total_time, (int, float))
