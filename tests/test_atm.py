import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm

# Тест 1: проверяем создание банкомата
def test_atm_creation():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    assert atm.id == 1
    assert atm.lat == 55.75
    assert atm.lon == 37.62

# Тест 2: проверяем сигнализацию переполнения
def test_atm_needs_service():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_in = 100
    assert atm.needs_service() == True
