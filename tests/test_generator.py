import sys
import os
import pytest

# Добавляем корневую папку проекта в путь поиска модулей
# Нужно, чтобы Python нашёл файлы generator.py и atm.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Проверяем, есть ли файл atm.py
if not os.path.exists('atm.py'):
    pytest.skip("atm.py ещё нет в main", allow_module_level=True)

# Импортируем функцию генерации банкоматов из файла Луизы
from generator import generate_atms

# Импортируем класс Atm (нужен для проверки, что генератор создаёт именно банкоматы)
from atm import Atm

# Тест 1: проверяет, что функция generate_atms возвращает список
def test_generate_atms_returns_list():
    # Генерируем 10 банкоматов
    atms = generate_atms(10)
    # Проверяем, что результат — это список
    assert isinstance(atms, list)
    # Проверяем, что в списке ровно 10 элементов
    assert len(atms) == 10

# Тест 2: проверяет, что каждый элемент списка — это объект класса Atm
def test_generate_atms_returns_atm_objects():
    # Генерируем 5 банкоматов
    atms = generate_atms(5)
    # Проверяем каждый банкомат: должен быть объектом класса Atm
    for atm in atms:
        assert isinstance(atm, Atm)
