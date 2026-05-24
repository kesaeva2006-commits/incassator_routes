import sys
import os
# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from atm import Atm
from generator import generate_atms
from greedy_algorithm import nearest_neighbor_route

def mock_travel_time(a, b, G, atm_to_node):
    """Простое расстояние по координатам вместо реального графа дорог"""
    return abs(a.lat - b.lat) + abs(a.lon - b.lon)

# ТЕСТЫ ДЛЯ ФУНКЦИИ nearest_neighbor_route
# Используем use_graph=False чтобы не грузить реальный граф Москвы в CI

@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_returns_list(mock_tt):
    """Проверяет что жадный алгоритм возвращает список"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert isinstance(route, list)

@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_contains_all_atms(mock_tt):
    """Проверяет что маршрут содержит все банкоматы из исходного списка"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert len(route) == len(atms)
    for atm in atms:
        assert atm in route

@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_no_duplicates(mock_tt):
    """Проверяет что в маршруте нет повторяющихся банкоматов"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert len(set(route)) == len(route)

@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_starts_with_first_atm_by_default(mock_tt):
    """Проверяет что по умолчанию маршрут начинается с первого банкомата"""
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert route[0] == atms[0]

@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_starts_with_given_start(mock_tt):
    """Проверяет что можно указать начальный банкомат"""
    atms = generate_atms(10)
    start = atms[5]
    route = nearest_neighbor_route(atms, start_atm=start, use_graph=False)
    assert route[0] == start

@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_empty_list(mock_tt):
    """Проверяет что при пустом списке возвращается пустой маршрут"""
    route = nearest_neighbor_route([], use_graph=False)
    assert route == []

@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_single_atm(mock_tt):
    """Проверяет что при одном банкомате маршрут состоит из него одного"""
    atms = generate_atms(1)
    route = nearest_neighbor_route(atms, use_graph=False)
    assert len(route) == 1
    assert route[0] == atms[0]


