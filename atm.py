import sys
import os

# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Теперь импортируем класс Atm из корневой папки
from atm import Atm

def test_atm_creation():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    assert atm.id == 1

def test_atm_needs_service():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_in = 100
    assert atm.needs_service() == True
