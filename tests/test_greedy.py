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

from unittest.mock import patch
import networkx as nx

def make_fake_graph_and_mapping(atms):
    """Создаёт простой граф-заглушку для тестов"""
    G = nx.complete_graph(len(atms), create_using=nx.DiGraph())
    for u, v in G.edges():
        G[u][v]['travel_time'] = 60
    atm_to_node = {atm.id: i for i, atm in enumerate(atms)}
    return G, atm_to_node

def make_atms(n):
    return [Atm(atm_id=i, lat=55.7 + i*0.01, lon=37.6 + i*0.01,
                capacity_in=10000, capacity_out=10000) for i in range(n)]

def test_build_time_matrix_returns_dict():
    from greedy_algorithm import build_time_matrix
    atms = make_atms(3)
    G = nx.complete_graph(3, create_using=nx.DiGraph())
    for u, v in G.edges():
        G[u][v]['travel_time'] = 60
    atm_to_node = {atm.id: i for i, atm in enumerate(atms)}
    matrix = build_time_matrix(atms, G, atm_to_node)
    assert isinstance(matrix, dict)

def test_build_time_matrix_self_distance_is_zero():
    from greedy_algorithm import build_time_matrix
    atms = make_atms(3)
    G = nx.complete_graph(3, create_using=nx.DiGraph())
    for u, v in G.edges():
        G[u][v]['travel_time'] = 60
    atm_to_node = {atm.id: i for i, atm in enumerate(atms)}
    matrix = build_time_matrix(atms, G, atm_to_node)
    for atm in atms:
        assert matrix[(atm.id, atm.id)] == 0

def test_build_time_matrix_unreachable_is_inf():
    from greedy_algorithm import build_time_matrix
    atms = make_atms(2)
    G = nx.DiGraph()
    G.add_node(0)
    G.add_node(1)
    atm_to_node = {atms[0].id: 0, atms[1].id: 1}
    matrix = build_time_matrix(atms, G, atm_to_node)
    assert matrix[(atms[0].id, atms[1].id)] == float('inf')

def test_nearest_neighbor_route_matrix_empty():
    from greedy_algorithm import nearest_neighbor_route_matrix
    result = nearest_neighbor_route_matrix([], nx.DiGraph(), {})
    assert result == []

def test_nearest_neighbor_route_matrix_returns_all():
    from greedy_algorithm import nearest_neighbor_route_matrix
    atms = generate_atms(4)
    G = nx.complete_graph(4, create_using=nx.DiGraph())
    for u, v in G.edges():
        G[u][v]['travel_time'] = 60
    atm_to_node = {atm.id: i for i, atm in enumerate(atms)}
    route = nearest_neighbor_route_matrix(atms, G, atm_to_node)
    assert len(route) == len(atms)


def test_travel_time_between_no_path():
    from greedy_algorithm import travel_time_between
    atms = generate_atms(2)
    G = nx.DiGraph()
    G.add_node(0)
    G.add_node(1)
    atm_to_node = {atms[0].id: 0, atms[1].id: 1}
    assert travel_time_between(atms[0], atms[1], G, atm_to_node) == float('inf')

