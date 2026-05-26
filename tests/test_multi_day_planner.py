"""
Тесты для модуля multi_day_planner.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from multi_day_planner import plan_multi_day


# ---------- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ----------

def make_test_atms(n=10):
    """Создаёт n тестовых банкоматов."""
    atms = []
    for i in range(n):
        atm = Atm(
            atm_id=i,
            lat=55.75 + i * 0.01,
            lon=37.62 + i * 0.01,
            capacity_in=100,
            capacity_out=100,
            mean_in=2,
            std_in=1,
            mean_out=3,
            std_out=1
        )
        atms.append(atm)  # append должен быть ВНУТРИ цикла!
    return atms


# ---------- plan_multi_day ----------

def test_plan_multi_day_returns_dict():
    atms = make_test_atms(10)
    plan = plan_multi_day(atms, days=3)
    assert isinstance(plan, dict)


def test_plan_multi_day_has_all_days():
    atms = make_test_atms(10)
    plan = plan_multi_day(atms, days=3)
    assert 1 in plan
    assert 2 in plan
    assert 3 in plan


def test_plan_multi_day_each_day_has_routes():
    atms = make_test_atms(10)
    plan = plan_multi_day(atms, days=3)
    for day in plan:
        assert "routes" in plan[day]
        assert "clusters" in plan[day]
        assert "queue" in plan[day]
        assert isinstance(plan[day]["routes"], list)
        assert isinstance(plan[day]["queue"], list)


def test_plan_multi_day_single_day():
    """Проверяем, что можно построить план на 1 день."""
    atms = make_test_atms(10)
    plan = plan_multi_day(atms, days=1)
    assert len(plan) == 1
    assert 1 in plan


def test_plan_multi_day_with_zero_atms():
    """Пустой список банкоматов не должен ломать функцию."""
    plan = plan_multi_day([], days=1)
    assert isinstance(plan, dict)