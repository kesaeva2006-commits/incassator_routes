import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from generator import generate_atms
from greedy_algorithm import nearest_neighbor_route, distance
generate_atms = generate_test_atms

# ТЕСТЫ ДЛЯ ФУНКЦИИ distance

def test_distance_returns_number():
    atm1 = Atm(1, 55.75, 37.62, 100, 100)
    atm2 = Atm(2, 55.76, 37.63, 100, 100)
    dist = distance(atm1, atm2)
    assert isinstance(dist, float)
    assert dist > 0

def test_distance_same_point_returns_zero():
    atm1 = Atm(1, 55.75, 37.62, 100, 100)
    atm2 = Atm(2, 55.75, 37.62, 100, 100)
    dist = distance(atm1, atm2)
    assert dist == 0

# ТЕСТЫ ДЛЯ ФУНКЦИИ nearest_neighbor_route

def test_nearest_neighbor_route_returns_list():
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert isinstance(route, list)

def test_nearest_neighbor_route_contains_all_atms():
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert len(route) == len(atms)
    # Проверяем, что все банкоматы из исходного списка есть в маршруте
    for atm in atms:
        assert atm in route

def test_nearest_neighbor_route_no_duplicates():
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    # Преобразуем во множество (оно не хранит дубликаты)
    # Если длина множества равна длине маршрута — повторов нет
    assert len(set(route)) == len(route)

def test_nearest_neighbor_route_starts_with_first_atm_by_default():
    atms = generate_atms(10)
    route = nearest_neighbor_route(atms)
    assert route[0] == atms[0]

def test_nearest_neighbor_route_starts_with_given_start():
    atms = generate_atms(10)
    start = atms[5]  # берём пятый банкомат
    route = nearest_neighbor_route(atms, start_atm=start)
    assert route[0] == start

def test_nearest_neighbor_route_empty_list():
    route = nearest_neighbor_route([])
    assert route == []

def test_nearest_neighbor_route_single_atm():
    atms = generate_atms(1)
    route = nearest_neighbor_route(atms)
    assert len(route) == 1
    assert route[0] == atms[0]
