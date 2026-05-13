import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from route_checker import check_all_routes, split_cluster, rebuild_routes_for_split_clusters
from atm import Atm

# ТЕСТЫ ДЛЯ check_all_routes

def test_check_all_routes_returns_dict():
    atms = [Atm(1, 55.75, 37.62, 100, 100), Atm(2, 55.76, 37.63, 100, 100)]
    clusters = [atms]
    routes = [atms]
    result = check_all_routes(clusters, routes)
    assert isinstance(result, dict)
    assert "ok" in result
    assert "over_limit" in result

# ТЕСТЫ ДЛЯ split_cluster

def test_split_cluster_returns_list():
    atms = [Atm(1, 55.75, 37.62, 100, 100), Atm(2, 55.76, 37.63, 100, 100)]
    result = split_cluster(atms)
    assert isinstance(result, list)

def test_split_cluster_handles_empty():
    result = split_cluster([])
    assert result == []

def test_split_cluster_single_atm():
    atms = [Atm(1, 55.75, 37.62, 100, 100)]
    result = split_cluster(atms)
    assert len(result) == 1
    assert len(result[0]) == 1

# ТЕСТЫ ДЛЯ rebuild_routes_for_split_clusters

def test_rebuild_routes_returns_list():
    atms = [Atm(1, 55.75, 37.62, 100, 100), Atm(2, 55.76, 37.63, 100, 100)]
    clusters = [atms]
    routes = [atms]
    check_result = {"ok": [0], "over_limit": []}
    result = rebuild_routes_for_split_clusters(clusters, routes, check_result)
    assert isinstance(result, list)
