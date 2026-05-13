import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from generator import generate_test_atms
from clustering import cluster_atms

# Алиас для краткости
generate_atms = generate_test_atms

# ТЕСТЫ ДЛЯ ФУНКЦИИ cluster_atms

def test_cluster_returns_correct_number_of_clusters():
    """Проверяет, что функция возвращает ровно n_clusters кластеров"""
    atms = generate_atms(100)
    clusters = cluster_atms(atms, n_clusters=5)
    assert len(clusters) == 5

def test_cluster_returns_list_of_lists():
    """Проверяет, что результат — список списков"""
    atms = generate_atms(100)
    clusters = cluster_atms(atms, n_clusters=5)
    assert isinstance(clusters, list)
    for cluster in clusters:
        assert isinstance(cluster, list)

def test_cluster_contains_all_atms():
    """Проверяет, что все банкоматы распределены по кластерам"""
    atms = generate_atms(100)
    clusters = cluster_atms(atms, n_clusters=5)
    
    # Собираем все банкоматы из кластеров в один список
    all_atms_in_clusters = []
    for cluster in clusters:
        all_atms_in_clusters.extend(cluster)
    
    # Проверяем, что количество совпадает
    assert len(all_atms_in_clusters) == len(atms)
    
    # Проверяем, что каждый банкомат из исходного списка есть в кластерах
    for atm in atms:
        assert atm in all_atms_in_clusters

def test_cluster_returns_different_clusters():
    """Проверяет, что кластеры разные (не пустые и не одинаковые)"""
    atms = generate_atms(100)
    clusters = cluster_atms(atms, n_clusters=5)
    
    # Проверяем, что есть хотя бы один непустой кластер
    non_empty = [c for c in clusters if len(c) > 0]
    assert len(non_empty) > 0

def test_cluster_empty_input():
    """Проверяет, что при пустом списке возвращаются пустые кластеры"""
    atms = []
    clusters = cluster_atms(atms, n_clusters=5)
    
    assert len(clusters) == 5
    for cluster in clusters:
        assert cluster == []

def test_cluster_few_atms():
    """Проверяет, что при количестве банкоматов меньше числа кластеров 
       некоторые кластеры остаются пустыми"""
    atms = generate_atms(3)  # всего 3 банкомата
    clusters = cluster_atms(atms, n_clusters=5)
    
    assert len(clusters) == 5
    # Суммарное количество банкоматов в кластерах равно 3
    total = sum(len(c) for c in clusters)
    assert total == 3

def test_cluster_deterministic_with_fixed_seed():
    """Проверяет, что при одинаковых входных данных результат одинаковый
       (благодаря random_state=42)"""
    atms1 = generate_atms(50)
    atms2 = generate_atms(50)
    
    clusters1 = cluster_atms(atms1, n_clusters=5)
    clusters2 = cluster_atms(atms2, n_clusters=5)
    
    # Длины кластеров должны совпадать
    sizes1 = [len(c) for c in clusters1]
    sizes2 = [len(c) for c in clusters2]
    assert sizes1 == sizes2
