import sys
import os

# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from generator import generate_atms  # Алиас: переименовываем для удобства
from greedy_algorithm import nearest_neighbor_route, distance

# ТЕСТЫ ДЛЯ ФУНКЦИИ distance

def test_distance_returns_number():
    """Проверяет, что расстояние между двумя банкоматами возвращает положительное число"""
    atm1 = Atm(1, 55.75, 37.62, 100, 100)
    atm2 = Atm(2, 55.76, 37.63, 100, 100)
    dist = distance(atm1, atm2)
    assert isinstance(dist, float)
    assert dist > 0

def test_distance_same_point_returns_zero():
    """Проверяет, что расстояние от банкомата до самого себя равно 0"""
    atm1 = Atm(1, 55.75, 37.62, 100, 100)
    atm2 = Atm(2, 55.75, 37.62, 100, 100)
    dist = distance(atm1, atm2)
    assert dist == 0

# ТЕСТЫ ДЛЯ ФУНКЦИИ nearest_neighbor_route

def test_nearest_neighbor_route_returns_list():
    """Проверяет, что жадный алгоритм возвращает список"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert isinstance(route, list)

def test_nearest_neighbor_route_contains_all_atms():
    """Проверяет, что маршрут содержит все банкоматы из исходного списка"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert len(route) == len(atms)
    for atm in atms:
        assert atm in route

def test_nearest_neighbor_route_no_duplicates():
    """Проверяет, что в маршруте нет повторяющихся банкоматов"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    # Если во множестве столько же элементов, сколько в маршруте — повторов нет
    assert len(set(route)) == len(route)

def test_nearest_neighbor_route_starts_with_first_atm_by_default():
    """Проверяет, что по умолчанию маршрут начинается с первого банкомата"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert route[0] == atms[0]

def test_nearest_neighbor_route_starts_with_given_start():
    """Проверяет, что можно указать начальный банкомат"""
    atms = generate_atms(10)
    start = atms[5]  # берём пятый банкомат
    route = nearest_neighbor_route(atms, start_atm=start)
    assert route[0] == start

def test_nearest_neighbor_route_empty_list():
    """Проверяет, что при пустом списке возвращается пустой маршрут"""
    route = nearest_neighbor_route([])
    assert route == []

def test_nearest_neighbor_route_single_atm():
    """Проверяет, что при одном банкомате маршрут состоит из него одного"""
    atms = generate_atms(1)
    route = nearest_neighbor_route(atms)
    assert len(route) == 1
    assert route[0] == atms[0]
