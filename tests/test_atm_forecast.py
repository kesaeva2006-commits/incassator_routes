import sys
import os
# Добавляем корневую папку в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm

# ТЕСТЫ ДЛЯ predict_level_after_hours

def test_predict_level_increases_over_time():
    """Проверяет что уровень приёма растёт со временем"""
    # Создаём банкомат с ненулевым средним приёма
    atm = Atm(1, 55.75, 37.62, 1000, 1000, mean_in=10, std_in=1, mean_out=5, std_out=1)
    pred_in_1h, _ = atm.predict_level_after_hours(1)
    pred_in_2h, _ = atm.predict_level_after_hours(2)
    # Через 2 часа уровень приёма должен быть выше чем через 1 час
    assert pred_in_2h > pred_in_1h

def test_predict_level_zero_hours():
    """Проверяет что через 0 часов уровни не изменились"""
    atm = Atm(1, 55.75, 37.62, 1000, 1000, mean_in=10, std_in=0, mean_out=5, std_out=0)
    pred_in, pred_out = atm.predict_level_after_hours(0)
    # Через 0 часов уровень приёма = текущий (0), выдача = полная (1000)
    assert pred_in == atm.current_in
    assert pred_out == atm.current_out

def test_predict_output_decreases_over_time():
    """Проверяет что уровень выдачи уменьшается со временем"""
    atm = Atm(1, 55.75, 37.62, 1000, 1000, mean_in=0, std_in=0, mean_out=10, std_out=1)
    _, pred_out_1h = atm.predict_level_after_hours(1)
    _, pred_out_2h = atm.predict_level_after_hours(2)
    # Через 2 часа денег в выдаче меньше чем через 1 час
    assert pred_out_2h < pred_out_1h

# ТЕСТЫ ДЛЯ is_critical

def test_is_critical_green_new_atm():
    """Новый банкомат с нулевой активностью должен быть GREEN"""
    atm = Atm(1, 55.75, 37.62, 1000, 1000, mean_in=0, std_in=0, mean_out=0, std_out=0)
    is_crit, status = atm.is_critical(hours_ahead=24)
    assert is_crit == False
    assert status == "GREEN"

def test_is_critical_red_overflow():
    """Банкомат с высоким приёмом должен стать RED_IN_OVERFLOW"""
    # mean_in=100 купюр/час, за 24 часа наберётся 2400 при ёмкости 1000 — точно переполнится
    atm = Atm(1, 55.75, 37.62, 1000, 1000, mean_in=100, std_in=0, mean_out=0, std_out=0)
    is_crit, status = atm.is_critical(hours_ahead=24)
    assert is_crit == True
    assert status == "RED_IN_OVERFLOW"

def test_is_critical_red_empty():
    """Банкомат с высоким снятием должен стать RED_OUT_EMPTY"""
    # mean_out=100 купюр/час, за 24 часа снимут 2400 при ёмкости 1000 — точно опустеет
    atm = Atm(1, 55.75, 37.62, 1000, 1000, mean_in=0, std_in=0, mean_out=100, std_out=0)
    is_crit, status = atm.is_critical(hours_ahead=24)
    assert is_crit == True
    assert status == "RED_OUT_EMPTY"

def test_is_critical_returns_tuple():
    """Проверяет что функция возвращает кортеж из двух элементов"""
    atm = Atm(1, 55.75, 37.62, 1000, 1000)
    result = atm.is_critical()
    assert isinstance(result, tuple)
    assert len(result) == 2
