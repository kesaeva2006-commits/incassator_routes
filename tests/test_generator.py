import sys
import os

# Добавляем корневую папку проекта в путь поиска модулей
# Нужно, чтобы Python мог найти файлы atm.py и generator.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from generator import generate_atms

# ТЕСТЫ ДЛЯ ФУНКЦИИ generate_atms

def test_generate_atms_returns_list():
    """Проверяет, что функция возвращает список"""
    atms = generate_atms(10)
    assert isinstance(atms, list)

def test_generate_atms_returns_correct_number():
    """Проверяет, что функция возвращает ровно запрошенное количество банкоматов"""
    # Проверка на 10 банкоматов (Спринт 1)
    atms = generate_atms(10)
    assert len(atms) == 10
    
    # Проверка на 100 банкоматов (для теста)
    atms = generate_atms(100)
    assert len(atms) == 100
    
    # Проверка на 1000 банкоматов (Спринт 2)
    atms = generate_atms(1000)
    assert len(atms) == 1000

def test_generate_atms_returns_atm_objects():
    """Проверяет, что каждый элемент списка — объект класса Atm"""
    atms = generate_atms(10)
    for atm in atms:
        assert isinstance(atm, Atm)

def test_generate_atms_returns_unique_ids():
    """Проверяет, что все банкоматы имеют уникальные ID"""
    atms = generate_atms(100)
    ids = [atm.id for atm in atms]
    # Преобразуем во множество: если есть дубликаты, длина множества будет меньше
    assert len(set(ids)) == len(ids)

def test_generate_atms_seed_consistency():
    """Проверяет, что при одинаковом seed генерируются одинаковые данные"""
    # Два запуска с одинаковым seed=42
    atms1 = generate_atms(5, seed=42)
    atms2 = generate_atms(5, seed=42)
    
    # Количество банкоматов должно совпадать
    assert len(atms1) == len(atms2)
    
    # Координаты и ёмкости должны быть одинаковыми
    for i in range(len(atms1)):
        assert atms1[i].lat == atms2[i].lat
        assert atms1[i].lon == atms2[i].lon
        assert atms1[i].capacity_in == atms2[i].capacity_in
        assert atms1[i].capacity_out == atms2[i].capacity_out

def test_generate_atms_different_seeds_produce_different_results():
    """Проверяет, что при разных seed генерируются разные данные"""
    atms1 = generate_atms(5, seed=42)
    atms2 = generate_atms(5, seed=100)
    
    # Хотя бы одно значение должно отличаться
    is_different = False
    for i in range(len(atms1)):
        if (atms1[i].lat != atms2[i].lat or 
            atms1[i].lon != atms2[i].lon or
            atms1[i].capacity_in != atms2[i].capacity_in or
            atms1[i].capacity_out != atms2[i].capacity_out):
            is_different = True
            break
    assert is_different == True

def test_generate_atms_coordinates_in_range():
    """Проверяет, что координаты банкоматов находятся в пределах Москвы"""
    atms = generate_atms(100)
    for atm in atms:
        # Широта Москвы: от 55.55 до 55.95
        assert 55.55 <= atm.lat <= 55.95
        # Долгота Москвы: от 37.30 до 37.95
        assert 37.30 <= atm.lon <= 37.95

def test_generate_atms_capacities_in_range():
    """Проверяет, что ёмкости бункеров находятся в заданных пределах"""
    atms = generate_atms(100)
    for atm in atms:
        # Бункер приёма: от 8000 до 30000 купюр
        assert 8000 <= atm.capacity_in <= 30000
        # Бункер выдачи: от 10000 до 25000 купюр
        assert 10000 <= atm.capacity_out <= 25000

def test_generate_atms_default_count():
    """Проверяет, что без указания количества генерируется 10 банкоматов"""
    atms = generate_atms()  # без параметров
    assert len(atms) == 10
