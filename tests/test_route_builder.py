import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from route_builder import build_routes_for_clusters

def make_atms(n, offset=0):
    return [Atm(atm_id=i+offset, lat=55.7 + i*0.01, lon=37.6 + i*0.01,
                capacity_in=10000, capacity_out=10000) for i in range(n)]

def test_build_routes_returns_list():
    clusters = [make_atms(3), make_atms(3, offset=10)]
    result = build_routes_for_clusters(clusters)
    assert isinstance(result, list)

def test_build_routes_correct_number():
    clusters = [make_atms(3), make_atms(3, offset=10), make_atms(3, offset=20)]
    result = build_routes_for_clusters(clusters)
    assert len(result) == 3

def test_build_routes_empty_cluster():
    clusters = [make_atms(3), [], make_atms(3, offset=10)]
    result = build_routes_for_clusters(clusters)
    assert result[1] == []

def test_build_routes_all_empty_clusters():
    result = build_routes_for_clusters([[], [], []])
    assert result == [[], [], []]

def test_build_routes_contains_all_atms():
    atms = make_atms(4)
    result = build_routes_for_clusters([atms])
    assert len(result[0]) == 4
    assert set(result[0]) == set(atms)
