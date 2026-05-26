import sys
import os
import time

# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator import generate_atms
from clustering import cluster_atms
from greedy_algorithm import nearest_neighbor_route

# ==============================================================
# ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ
# Задача: 1000 банкоматов, 5 кластеров, маршруты — всё < 30 секунд
# ==============================================================

def test_generate_1000_atms_performance():
    """Генерация 1000 банкоматов должна занимать < 5 секунд"""
    start = time.time()
    atms = generate_atms(1000)
    elapsed = time.time() - start
    assert len(atms) == 1000
    assert elapsed < 5

def test_cluster_1000_atms_performance():
    """Кластеризация 1000 банкоматов на 5 кластеров должна занимать < 10 секунд"""
    atms = generate_atms(1000)
    start = time.time()
    clusters = cluster_atms(atms, n_clusters=5)
    elapsed = time.time() - start
    assert len(clusters) == 5
    assert elapsed < 10

def test_full_pipeline_1000_atms_under_30_seconds():
    """
    ГЛАВНЫЙ ТЕСТ: полный пайплайн для 1000 банкоматов должен завершаться < 30 секунд.
    Пайплайн: генерация → кластеризация → маршруты для каждого кластера
    """
    start = time.time()
    atms = generate_atms(1000)
    clusters = cluster_atms(atms, n_clusters=5)
    routes = []
    for cluster in clusters:
        if cluster:
            # use_graph=False — быстрый режим без загрузки графа дорог (для CI)
            route = nearest_neighbor_route(cluster, use_graph=False)
            routes.append(route)
    elapsed = time.time() - start
    assert len(routes) == 5
    assert sum(len(r) for r in routes) == 1000
    assert elapsed < 30, f"Пайплайн занял {elapsed:.2f}с — превышен лимит 30 секунд!"
    print(f"\n Пайплайн 1000 банкоматов выполнен за {elapsed:.2f}с")

