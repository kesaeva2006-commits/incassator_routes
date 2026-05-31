"""
Тесты для модуля route_checker.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from route_checker import check_all_routes, get_route_time, rebalance_clusters


# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

def make_atm(atm_id, lat=55.75, lon=37.62):
    """Быстрое создание банкомата для тестов."""
    return Atm(atm_id, lat + atm_id * 0.01, lon + atm_id * 0.01,
               100, 100, mean_in=1, std_in=0, mean_out=1, std_out=0)


def make_small_route(n=3):
    """Создаёт тестовый маршрут из n банкоматов."""
    return [make_atm(i) for i in range(n)]


# ---------- check_all_routes ----------

def test_check_all_routes_returns_dict():
    clusters = [[make_atm(1), make_atm(2)]]
    routes = [make_small_route(2)]
    result = check_all_routes(clusters, routes)
    assert isinstance(result, dict)
    assert "ok" in result
    assert "over_limit" in result


def test_check_all_routes_small_route_is_ok():
    """Маленький маршрут должен укладываться в 8 часов."""
    clusters = [[make_atm(1), make_atm(2)]]
    routes = [make_small_route(2)]
    result = check_all_routes(clusters, routes)
    assert 0 in result["ok"]
    assert len(result["over_limit"]) == 0


# ---------- get_route_time ----------

def test_get_route_time_returns_number():
    route = make_small_route(2)
    time = get_route_time(route)
    assert isinstance(time, (int, float))
    assert time > 0


def test_get_route_time_single_atm():
    route = [make_atm(1)]
    time = get_route_time(route)
    assert time == 45  # 0 в пути + 15 обслуживание + 30 резерв


# ---------- rebalance_clusters ----------

def test_rebalance_clusters_returns_tuple():
    clusters = [[make_atm(i) for i in range(5)]]
    routes = [make_small_route(5)]
    check_result = {"ok": [], "over_limit": [0]}

    result = rebalance_clusters(clusters, routes, check_result)
    assert isinstance(result, tuple)
    assert len(result) == 3  # new_clusters, new_routes, queue


def test_rebalance_clusters_handles_over_limit():
    """Проверяем, что перераспределение не падает на проблемном кластере."""
    # Создаём кластер из 30 банкоматов — заведомо не влезет
    atms = [make_atm(i) for i in range(30)]
    clusters = [atms[:15], atms[15:]]

    from greedy_algorithm import nearest_neighbor_route
    routes = [nearest_neighbor_route(c) if len(c) >= 2 else c for c in clusters]
    check_result = check_all_routes(clusters, routes)

    if check_result["over_limit"]:
        new_clusters, new_routes, queue = rebalance_clusters(clusters, routes, check_result)
        assert isinstance(new_clusters, list)
        assert isinstance(new_routes, list)
        assert isinstance(queue, list)