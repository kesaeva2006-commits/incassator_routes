import sys
import os

# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm

# ТЕСТЫ ДЛЯ КОНСТРУКТОРА И БАЗОВЫХ ПАРАМЕТРОВ

def test_atm_creation():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    assert atm.id == 1
    assert atm.lat == 55.75
    assert atm.lon == 37.62
    assert atm.capacity_in == 100
    assert atm.capacity_out == 100

def test_atm_creation_with_stats():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=10, std_in=2, mean_out=15, std_out=3)
    assert atm.mean_in == 10
    assert atm.std_in == 2
    assert atm.mean_out == 15
    assert atm.std_out == 3

def test_atm_initial_state():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    assert atm.current_in == 0
    assert atm.current_out == 100

def test_atm_invalid_capacity():
    try:
        atm = Atm(1, 55.75, 37.62, 0, 100)
        assert False, "Должна быть ошибка при capacity_in <= 0"
    except ValueError:
        pass

# ТЕСТЫ ДЛЯ МЕТОДА needs_service

def test_needs_service_true_when_in_full():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_in = 100  # 100% заполнения
    assert atm.needs_service() == True

def test_needs_service_true_when_in_at_90_percent():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_in = 90  # 90% заполнения
    assert atm.needs_service() == True

def test_needs_service_false_when_in_below_90():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_in = 89
    assert atm.needs_service() == False

def test_needs_service_true_when_out_empty():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_out = 0
    assert atm.needs_service() == True

def test_needs_service_true_when_out_at_10_percent():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_out = 10  # 10% осталось
    assert atm.needs_service() == True

def test_needs_service_false_when_out_above_10():
    atm = Atm(1, 55.75, 37.62, 100, 100)
    atm.current_out = 11
    assert atm.needs_service() == False

# ТЕСТЫ ДЛЯ МЕТОДА predict_level_after_hours

def test_predict_returns_floats():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=10, std_in=2, mean_out=15, std_out=3)
    pred_in, pred_out = atm.predict_level_after_hours(24)
    assert isinstance(pred_in, (int, float))
    assert isinstance(pred_out, (int, float))

def test_predict_with_zero_stats():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=0, std_out=0)
    pred_in, pred_out = atm.predict_level_after_hours(24)
    assert pred_in == 0
    assert pred_out == 100  # current_out = capacity_out = 100
    
# ТЕСТЫ ДЛЯ МЕТОДА is_critical

def test_is_critical_returns_tuple():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=10, std_in=2, mean_out=15, std_out=3)
    is_crit, reason = atm.is_critical(24)
    assert isinstance(is_crit, bool)
    assert isinstance(reason, str)

def test_is_critical_green_when_normal():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=1, std_in=0, mean_out=1, std_out=0)
    is_crit, reason = atm.is_critical(24)
    assert is_crit == False
    assert reason == "GREEN"

def test_is_critical_red_in_overflow():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=100, std_in=0, mean_out=0, std_out=0)
    is_crit, reason = atm.is_critical(24)
    assert is_crit == True
    assert reason == "RED_IN_OVERFLOW"

def test_is_critical_red_out_empty():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=100, std_out=0)
    is_crit, reason = atm.is_critical(24)
    assert is_crit == True
    assert reason == "RED_OUT_EMPTY"

def test_is_critical_yellow_warning():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=3, std_in=0, mean_out=0, std_out=0)
    # Через 24 часа: pred_in = 0 + 3*24 = 72 (72% от 100)
    is_crit, reason = atm.is_critical(24)
    assert is_crit == True
    assert reason == "YELLOW"
