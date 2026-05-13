import sys
import os

# Добавляем корневую папку в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm

def test_atm_creation():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    assert atm.id == 1
    assert atm.lat == 55.75
    assert atm.lon == 37.62

def test_atm_needs_service_true_when_full():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_in = 100
    assert atm.needs_service() == True

def test_atm_needs_service_false_when_not_full():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_in = 80
    assert atm.needs_service() == False
