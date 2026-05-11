import sys
import os
import pytest

# Проверяем, есть ли файл atm.py
if not os.path.exists('atm.py'):
    pytest.skip("atm.py ещё нет в main, тест будет включён после вливания кода", allow_module_level=True)

# Добавляем корневую папку проекта (на уровень выше папки tests)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm

def test_atm_creation():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    assert atm.id == 1
    assert atm.lat == 55.75
    assert atm.lon == 37.62

def test_atm_needs_service():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_in = 100
    assert atm.needs_service() == True
