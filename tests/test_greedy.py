import sys
import os
# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock  # инструменты для подмены тяжёлых функций
from atm import Atm
from generator import generate_atms  # импортируем функцию генерации банкоматов
from greedy_algorithm import nearest_neighbor_route

# Заглушка вместо реального времени по карте Москвы
def mock_travel_time(a, b, G, atm_to_node):
    """Простое расстояние по координатам вместо реального графа дорог"""
    return abs(a.lat - b.lat) + abs(a.lon - b.lon)

# ТЕСТЫ ДЛЯ ФУНКЦИИ nearest_neighbor_route

@patch('greedy_algorithm.load_moscow_graph')
@patch('greedy_algorithm.match_atms_to_nodes')
@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_returns_list(mock_tt, mock_match, mock_graph):
    """Проверяет что жадный алгоритм возвращает список"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert isinstance(route, list)

@patch('greedy_algorithm.load_moscow_graph')
@patch('greedy_algorithm.match_atms_to_nodes')
@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_contains_all_atms(mock_tt, mock_match, mock_graph):
    """Проверяет что маршрут содержит все банкоматы из исходного списка"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert len(route) == len(atms)
    for atm in atms:
        assert atm in route

@patch('greedy_algorithm.load_moscow_graph')
@patch('greedy_algorithm.match_atms_to_nodes')
@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_no_duplicates(mock_tt, mock_match, mock_graph):
    """Проверяет что в маршруте нет повторяющихся банкоматов"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    # Если во множестве столько же элементов сколько в маршруте — повторов нет
    assert len(set(route)) == len(route)

@patch('greedy_algorithm.load_moscow_graph')
@patch('greedy_algorithm.match_atms_to_nodes')
@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_starts_with_first_atm_by_default(mock_tt, mock_match, mock_graph):
    """Проверяет что по умолчанию маршрут начинается с первого банкомата"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert route[0] == atms[0]

@patch('greedy_algorithm.load_moscow_graph')
@patch('greedy_algorithm.match_atms_to_nodes')
@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_starts_with_given_start(mock_tt, mock_match, mock_graph):
    """Проверяет что можно указать начальный банкомат"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = generate_atms(10)
    start = atms[5]  # берём пятый банкомат
    route = nearest_neighbor_route(atms, start_atm=start)
    assert route[0] == start

@patch('greedy_algorithm.load_moscow_graph')
@patch('greedy_algorithm.match_atms_to_nodes')
@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_empty_list(mock_tt, mock_match, mock_graph):
    """Проверяет что при пустом списке возвращается пустой маршрут"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    route = nearest_neighbor_route([])
    assert route == []

@patch('greedy_algorithm.load_moscow_graph')
@patch('greedy_algorithm.match_atms_to_nodes')
@patch('greedy_algorithm.travel_time_between', side_effect=mock_travel_time)
def test_nearest_neighbor_route_single_atm(mock_tt, mock_match, mock_graph):
    """Проверяет что при одном банкомате маршрут состоит из него одного"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = generate_atms(1)
    route = nearest_neighbor_route(atms)
    assert len(route) == 1
    assert route[0] == atms[0]
