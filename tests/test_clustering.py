import sys
import os

# Добавляем корневую папку проекта в путь поиска модулей
# Чтобы Python мог найти файлы atm.py, generator.py, clustering.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем класс Atm (нужен для проверки типов)
from atm import Atm

# Импортируем функцию генерации банкоматов (из файла Луизы)
from generator import generate_atms

# Импортируем функцию кластеризации (которую тестируем)
from clustering import cluster_atms


# Тест 1: проверяет, что функция возвращает ровно 5 кластеров
def test_cluster_returns_correct_number_of_clusters():
    # Генерируем 100 банкоматов для теста
    atms = generate_atms(100)
    
    # Выполняем кластеризацию на 5 групп
    clusters = cluster_atms(atms, n_clusters=5)
    
    # Проверяем, что получилось ровно 5 кластеров
    assert len(clusters) == 5


# Тест 2: проверяет, что результат — это список списков
def test_cluster_returns_list_of_lists():
    atms = generate_atms(100)
    clusters = cluster_atms(atms, n_clusters=5)
    
    # Результат должен быть списком
    assert isinstance(clusters, list)
    
    # Каждый элемент внутри — тоже список
    for cluster in clusters:
        assert isinstance(cluster, list)


# Тест 3: проверяет, что все банкоматы распределены по кластерам
def test_cluster_contains_all_atms():
    atms = generate_atms(100)
    clusters = cluster_atms(atms, n_clusters=5)
    
    # Собираем все банкоматы из кластеров в один список
    all_atms_in_clusters = []
    for cluster in clusters:
        all_atms_in_clusters.extend(cluster)
    
    # Количество банкоматов в кластерах должно совпадать с исходным
    assert len(all_atms_in_clusters) == len(atms)
    
    # Каждый исходный банкомат должен быть в каком-то кластере
    for atm in atms:
        assert atm in all_atms_in_clusters


# Тест 4: проверяет, что функция работает с пустым списком
def test_cluster_empty_input():
    atms = []
    clusters = cluster_atms(atms, n_clusters=5)
    
    # Должно вернуться 5 пустых кластеров
    assert len(clusters) == 5
    for cluster in clusters:
        assert cluster == []


# Тест 5: проверяет, что когда банкоматов меньше 5,
#         некоторые кластеры остаются пустыми
def test_cluster_few_atms():
    # Генерируем всего 3 банкомата
    atms = generate_atms(3)
    clusters = cluster_atms(atms, n_clusters=5)
    
    # Всего 5 кластеров
    assert len(clusters) == 5
    
    # Суммарное количество банкоматов в кластерах = 3
    total = sum(len(c) for c in clusters)
    assert total == 3
