import sys
import os
# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем функцию вывода маршрута из файла route_printer.py
from route_printer import print_route

# Импортируем генератор банкоматов (чтобы создать тестовые данные)
from generator import generate_atms

# Тест: проверяет, что функция print_route существует и не падает при вызове
def test_print_route_exists():
    # Генерируем 3 тестовых банкомата
    atms = generate_atms(3)
    # Вызываем функцию (она должна вывести маршрут в консоль)
    result = print_route(atms)
    # Функция ничего не возвращает (только печатает), поэтому result = None
    # Проверяем, что вызов не сломался
    assert result is None or result == None
