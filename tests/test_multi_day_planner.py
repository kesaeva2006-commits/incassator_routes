# tests/test_multi_day_planner.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from multi_day_planner import plan_multi_day

def make_test_atms(n):
    """Создает тестовые банкоматы"""
    atms = []
    for i in range(n):
        atm = Atm(
            atm_id=i,
            lat=55.7 + i * 0.01,
            lon=37.6 + i * 0.01,
            capacity_in=10000,
            capacity_out=10000,
            mean_in=100,  # среднее поступление в час
            std_in=20,
            mean_out=80,   # средняя выдача в час
            std_out=15
        )
        atm.current_in = 0
        atm.current_out = 5000  # начальный уровень
        atms.append(atm)
    return atms

def test_plan_multi_day_returns_dict():
    """Проверяет, что plan_multi_day возвращает словарь"""
    atms = make_test_atms(10)
    result = plan_multi_day(atms, days=3)
    assert isinstance(result, dict)

def test_plan_multi_day_has_all_days():
    """Проверяет, что результат содержит все дни (1, 2, 3)"""
    atms = make_test_atms(10)
    result = plan_multi_day(atms, days=3)
    expected_days = {1, 2, 3}
    assert set(result.keys()) == expected_days

def test_plan_multi_day_each_day_has_routes():
    """Проверяет, что каждый день содержит маршруты"""
    atms = make_test_atms(10)
    result = plan_multi_day(atms, days=3)
    
    for day, data in result.items():
        assert "routes" in data
        assert "clusters" in data
        assert "queue" in data
        assert isinstance(data["routes"], list)
        assert isinstance(data["clusters"], list)
        assert isinstance(data["queue"], list)

def test_plan_multi_day_single_day():
    """Проверяет работу с одним днем"""
    atms = make_test_atms(10)
    result = plan_multi_day(atms, days=1)
    
    assert len(result) == 1
    assert 1 in result
    assert "routes" in result[1]

def test_plan_multi_day_with_zero_atms():
    """Проверяет работу с пустым списком банкоматов"""
    result = plan_multi_day([], days=3)
    
    assert isinstance(result, dict)
    assert len(result) == 3  # 3 дня, но все маршруты пустые
    
    for day, data in result.items():
        assert data["routes"] == [] or all(len(r) == 0 for r in data["routes"])

def test_plan_multi_day_updates_levels():
    """Проверяет, что уровни банкоматов обновляются между днями"""
    atms = make_test_atms(5)
    
    # Сохраняем начальные уровни
    initial_levels = [(atm.current_in, atm.current_out) for atm in atms]
    
    # Запускаем планирование
    result = plan_multi_day(atms, days=2)
    
    # Уровни должны измениться после первого дня
    # (проверяем, что хотя бы один банкомат изменил уровни)
    levels_changed = False
    for i, atm in enumerate(atms):
        if atm.current_in != initial_levels[i][0] or atm.current_out != initial_levels[i][1]:
            levels_changed = True
            break
    
    assert levels_changed, "Уровни банкоматов должны обновиться после первого дня"
