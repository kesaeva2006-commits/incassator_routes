import sys
import os
# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем жадный алгоритм (функция называется nearest_neighbor_route, а не nearest_neighbor)
from greedy_algorithm import nearest_neighbor_route

# Импортируем генератор банкоматов (функцию generate_atms — уточни у Луизы точное имя)
from generator import generate_atms

# Тест 1: проверяет, что маршрут — это список, и он содержит все банкоматы
def test_nearest_neighbor_route_returns_list():
    # Генерируем 10 банкоматов
    atms = generate_atms(10)
    # Строим маршрут жадным алгоритмом
    route = nearest_neighbor_route(atms)
    # Проверяем, что маршрут — это список
    assert isinstance(route, list)
    # Проверяем, что маршрут содержит все 10 банкоматов
    assert len(route) == len(atms)

# Тест 2: проверяет, что в маршруте нет повторяющихся банкоматов
def test_nearest_neighbor_route_no_duplicates():
    # Генерируем 10 банкоматов
    atms = generate_atms(10)
    # Строим маршрут
    route = nearest_neighbor_route(atms)
    # Преобразуем маршрут во множество (оно не хранит дубликаты)
    # Если длина множества равна длине маршрута — значит, повторов нет
    assert len(set(route)) == len(route)
