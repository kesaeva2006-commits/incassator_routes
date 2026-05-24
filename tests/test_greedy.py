import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from generator import generate_atms
from greedy_algorithm import nearest_neighbor_route

# ТЕСТЫ ДЛЯ ФУНКЦИИ nearest_neighbor_route
# Используем use_graph=False чтобы не грузить реальный граф Москвы в CI

def test_nearest_neighbor_route_returns_list():
    """Проверяет что жадный алгоритм возвращает список"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert isinstance(route, list)

def test_nearest_neighbor_route_contains_all_atms():
    """Проверяет что маршрут содержит все банкоматы из исходного списка"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert len(route) == len(atms)
    for atm in atms:
        assert atm in route

def test_nearest_neighbor_route_no_duplicates():
    """Проверяет что в маршруте нет повторяющихся банкоматов"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert len(set(route)) == len(route)

def test_nearest_neighbor_route_starts_with_first_atm_by_default():
    """Проверяет что по умолчанию маршрут начинается с первого банкомата"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert route[0] == atms[0]

def test_nearest_neighbor_route_starts_with_given_start():
    """Проверяет что можно указать начальный банкомат"""
    atms = generate_atms(10)
    start = atms[5]
    route = nearest_neighbor_route(atms, start_atm=start, use_graph=False)
    assert route[0] == start

def test_nearest_neighbor_route_empty_list():
    """Проверяет что при пустом списке возвращается пустой маршрут"""
    route = nearest_neighbor_route([], use_graph=False)
    assert route == []

def test_nearest_neighbor_route_single_atm():
    """Проверяет что при одном банкомате маршрут состоит из него одного"""
    atms = generate_atms(1)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert len(route) == 1
    assert route[0] == atms[0]
