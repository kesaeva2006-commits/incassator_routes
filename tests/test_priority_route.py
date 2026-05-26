"""
Тесты для модуля priority_route.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from priority_route import sort_by_priority, build_priority_route, print_priority_summary


# ---------- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ----------

def make_atm(atm_id, mean_in=0, mean_out=0, capacity_in=100, capacity_out=100):
    """Создаёт банкомат с заданными параметрами для тестов."""
    atm = Atm(atm_id, 55.75 + atm_id * 0.01, 37.62 + atm_id * 0.01,
              capacity_in, capacity_out,
              mean_in=mean_in, std_in=0,
              mean_out=mean_out, std_out=0)
    return atm


# ---------- sort_by_priority ----------

def test_sort_by_priority_returns_list():
    atms = [make_atm(1), make_atm(2)]
    result = sort_by_priority(atms)
    assert isinstance(result, list)
    assert len(result) == 2


def test_sort_by_priority_red_first():
    # Красный банкомат должен быть первым
    red = make_atm(1, mean_in=100)  # Забьётся за 24ч → RED
    green = make_atm(2, mean_in=1, mean_out=1)  # Норма → GREEN

    sorted_atms = sort_by_priority([green, red])
    assert sorted_atms[0].id == red.id


def test_sort_by_priority_yellow_before_green():
    yellow = make_atm(1, mean_in=3)  # 72% за 24ч → YELLOW
    green = make_atm(2, mean_in=1, mean_out=1)  # GREEN

    sorted_atms = sort_by_priority([green, yellow])
    assert sorted_atms[0].id == yellow.id


def test_sort_by_priority_preserves_order_within_group():
    # Банкоматы одного цвета сохраняют порядок
    green1 = make_atm(1, mean_in=1)
    green2 = make_atm(2, mean_in=1)

    sorted_atms = sort_by_priority([green1, green2])
    assert sorted_atms[0].id == 1
    assert sorted_atms[1].id == 2


def test_sort_by_priority_empty_list():
    result = sort_by_priority([])
    assert result == []


# ---------- build_priority_route ----------

def test_build_priority_route_returns_list():
    atms = [make_atm(1), make_atm(2)]
    route = build_priority_route(atms)
    assert isinstance(route, list)
    assert len(route) == 2


def test_build_priority_route_single_atm():
    atm = make_atm(1)
    route = build_priority_route([atm])
    assert route == [atm]


def test_build_priority_route_empty():
    route = build_priority_route([])
    assert route == []


def test_build_priority_route_starts_with_red():
    red = make_atm(1, mean_in=100)  # RED
    green1 = make_atm(2, mean_in=1)  # GREEN
    green2 = make_atm(3, mean_in=1)  # GREEN

    route = build_priority_route([green1, green2, red])
    # Первым должен быть красный
    assert route[0].id == red.id


# ---------- print_priority_summary ----------

def test_print_priority_summary_runs():
    """Проверяем, что функция не падает с ошибкой."""
    atms = [make_atm(1, mean_in=1), make_atm(2, mean_in=3), make_atm(3, mean_in=100)]
    try:
        print_priority_summary(atms)
    except Exception as e:
        assert False, f"Функция упала с ошибкой: {e}"