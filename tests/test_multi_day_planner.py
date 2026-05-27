"""
Тесты для модуля multi_day_planner.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch
import networkx as nx
from atm import Atm
from multi_day_planner import plan_multi_day

# ---------- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ----------
def make_test_atms(n=10):
    atms = []
    for i in range(n):
        atm = Atm(
            atm_id=i,
            lat=55.75 + i * 0.01,
            lon=37.62 + i * 0.01,
            capacity_in=100,
            capacity_out=100,
            mean_in=2,
            std_in=1,
            mean_out=3,
            std_out=1
        )
        atms.append(atm)
    return atms

def make_fake_graph(atms):
    """Создаёт граф-заглушку для тестов."""
    n = len(atms)
    G = nx.complete_graph(n, create_using=nx.DiGraph())
    for u, v in G.edges():
        G[u][v]['travel_time'] = 60
    atm_to_node = {atm.id: i for i, atm in enumerate(atms)}
    return G, atm_to_node

# ---------- plan_multi_day ----------
def test_plan_multi_day_returns_dict():
    atms = make_test_atms(10)
    G, atm_to_node = make_fake_graph(atms)
    with patch('greedy_algorithm.load_moscow_graph', return_value=G), \
         patch('greedy_algorithm.match_atms_to_nodes', return_value=atm_to_node):
        plan = plan_multi_day(atms, days=3)
    assert isinstance(plan, dict)

def test_plan_multi_day_has_all_days():
    atms = make_test_atms(10)
    G, atm_to_node = make_fake_graph(atms)
    with patch('greedy_algorithm.load_moscow_graph', return_value=G), \
         patch('greedy_algorithm.match_atms_to_nodes', return_value=atm_to_node):
        plan = plan_multi_day(atms, days=3)
    assert 1 in plan
    assert 2 in plan
    assert 3 in plan

def test_plan_multi_day_each_day_has_routes():
    atms = make_test_atms(10)
    G, atm_to_node = make_fake_graph(atms)
    with patch('greedy_algorithm.load_moscow_graph', return_value=G), \
         patch('greedy_algorithm.match_atms_to_nodes', return_value=atm_to_node):
        plan = plan_multi_day(atms, days=3)
    for day in plan:
        assert "routes" in plan[day]
        assert "clusters" in plan[day]
        assert "queue" in plan[day]
        assert isinstance(plan[day]["routes"], list)
        assert isinstance(plan[day]["queue"], list)

def test_plan_multi_day_single_day():
    atms = make_test_atms(10)
    G, atm_to_node = make_fake_graph(atms)
    with patch('greedy_algorithm.load_moscow_graph', return_value=G), \
         patch('greedy_algorithm.match_atms_to_nodes', return_value=atm_to_node):
        plan = plan_multi_day(atms, days=1)
    assert len(plan) == 1
    assert 1 in plan

def test_plan_multi_day_with_zero_atms():
    plan = plan_multi_day([], days=1)
    assert isinstance(plan, dict)
