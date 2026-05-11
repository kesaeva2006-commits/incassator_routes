import sys
import os
# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем жадный алгоритм из файла Луизы
from greedy_algorithm import nearest_neighbor

# Импортируем генератор банкоматов (чтобы создать тестовые данные)
from generator import generate_atms

# Тест 1: проверяет, что маршрут начинается с правильного банкомата и не теряет банкоматы
def test_nearest_neighbor_returns_route():
    # Генерируем 10 банкоматов
    atms = generate_atms(10)
    # Начинаем маршрут с первого банкомата в списке
    start = atms[0]
    # Строим маршрут
    route = nearest_neighbor(atms, start)
    
    # Проверяем, что маршрут — это список
    assert isinstance(route, list)
    # Проверяем, что маршрут содержит все 10 банкоматов
    assert len(route) == len(atms)
    # Проверяем, что маршрут начинается с того банкомата, который мы указали
    assert route[0] == start

# Тест 2: проверяет, что в маршруте нет повторяющихся банкоматов
def test_nearest_neighbor_no_duplicates():
    # Генерируем 10 банкоматов
    atms = generate_atms(10)
    start = atms[0]
    route = nearest_neighbor(atms, start)
    
    # Преобразуем маршрут во множество (оно не хранит дубликаты)
    # Если длина множества равна длине маршрута — значит, повторов нет
    assert len(set(route)) == len(route)
