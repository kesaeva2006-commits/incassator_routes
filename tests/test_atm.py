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

# ============================================================
# НОВЫЕ ТЕСТЫ — СПРИНТ 3 (методы бункера)
# Добавлены: predict_inflow, predict_outflow,
#            get_risk_level, update_levels
# ============================================================
 
 
# ------ predict_inflow ------
# Метод считает, сколько купюр накопится в бункере ПРИЁМА через N часов.
# Формула: current_in + mean_in * hours + 2 * std_in * sqrt(hours)
 
def test_predict_inflow_returns_float():
    # Проверяем, что метод вообще возвращает число
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=10, std_in=2, mean_out=0, std_out=0)
    result = atm.predict_inflow(24)
    assert isinstance(result, (int, float))
 
def test_predict_inflow_zero_stats():
    # Если mean_in=0 и std_in=0 — никто ничего не вносил, бункер приёма остаётся пустым
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=0, std_out=0)
    result = atm.predict_inflow(24)
    assert result == 0
 
def test_predict_inflow_correct_value():
    # mean_in=2, std_in=0, hours=10 => 0 + 2*10 + 0 = 20
    # Проверяем, что математика считается правильно
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=2, std_in=0, mean_out=0, std_out=0)
    result = atm.predict_inflow(10)
    assert result == 20
 
def test_predict_inflow_grows_with_time():
    # Чем больше часов прошло — тем больше купюр накопилось в бункере приёма
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=5, std_in=0, mean_out=0, std_out=0)
    result_12 = atm.predict_inflow(12)
    result_24 = atm.predict_inflow(24)
    assert result_24 > result_12
 
def test_predict_inflow_with_nonzero_current():
    # Если бункер приёма уже не пустой (current_in=30),
    # прогноз должен учитывать это: 30 + 2*10 = 50
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=2, std_in=0, mean_out=0, std_out=0)
    atm.current_in = 30
    result = atm.predict_inflow(10)
    assert result == 50
 
 
# ------ predict_outflow ------
# Метод считает, сколько денег ОСТАНЕТСЯ в бункере ВЫДАЧИ через N часов.
# Формула: current_out - (mean_out * hours + 2 * std_out * sqrt(hours))
 
def test_predict_outflow_returns_float():
    # Проверяем, что метод возвращает число
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=5, std_out=1)
    result = atm.predict_outflow(24)
    assert isinstance(result, (int, float))
 
def test_predict_outflow_zero_stats():
    # Если mean_out=0 — никто ничего не снимал, бункер выдачи полный
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=0, std_out=0)
    result = atm.predict_outflow(24)
    assert result == 100
 
def test_predict_outflow_correct_value():
    # mean_out=3, std_out=0, hours=10 => 100 - 3*10 = 70
    # Проверяем правильность расчёта
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=3, std_out=0)
    result = atm.predict_outflow(10)
    assert result == 70
 
def test_predict_outflow_decreases_with_time():
    # Чем больше часов — тем меньше денег осталось в бункере выдачи
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=5, std_out=0)
    result_12 = atm.predict_outflow(12)
    result_24 = atm.predict_outflow(24)
    assert result_24 < result_12
 
 
# ------ get_risk_level ------
# Метод возвращает уровень риска: "GREEN", "YELLOW" или "RED".
# RED   — бункер приёма >90% или выдача <10%
# YELLOW — приём >70% или выдача <30%
# GREEN  — всё в норме
 
def test_get_risk_level_returns_string():
    # Проверяем, что метод возвращает строку
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=5, std_in=0, mean_out=5, std_out=0)
    result = atm.get_risk_level(24)
    assert isinstance(result, str)
 
def test_get_risk_level_green():
    # mean_in=1, mean_out=1 — через 24ч приём=24%, выдача=76% — всё в норме
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=1, std_in=0, mean_out=1, std_out=0)
    result = atm.get_risk_level(24)
    assert result == "GREEN"
 
def test_get_risk_level_red_in_overflow():
    # mean_in=100 — за 24ч приём забьётся до 2400% от capacity => RED
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=100, std_in=0, mean_out=0, std_out=0)
    result = atm.get_risk_level(24)
    assert result == "RED"
 
def test_get_risk_level_red_out_empty():
    # mean_out=100 — за 24ч выдача опустеет до нуля => RED
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=100, std_out=0)
    result = atm.get_risk_level(24)
    assert result == "RED"
 
def test_get_risk_level_yellow():
    # mean_in=3, hours=24 => pred_in = 3*24 = 72 (72% > 70%) => YELLOW
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=3, std_in=0, mean_out=0, std_out=0)
    result = atm.get_risk_level(24)
    assert result == "YELLOW"
 
 
# ------ update_levels ------
# Метод обновляет РЕАЛЬНЫЕ текущие уровни бункеров после прошедшего времени.
# В отличие от predict_* — он меняет сам объект (current_in и current_out).
 
def test_update_levels_increases_current_in():
    # После 10 часов с mean_in=5: current_in = 0 + 5*10 = 50
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=5, std_in=0, mean_out=0, std_out=0)
    atm.update_levels(10)
    assert atm.current_in == 50
 
def test_update_levels_decreases_current_out():
    # После 10 часов с mean_out=3: current_out = 100 - 3*10 = 70
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=3, std_out=0)
    atm.update_levels(10)
    assert atm.current_out == 70
 
def test_update_levels_current_in_not_exceed_capacity():
    # mean_in=50 за 24ч = 1200 купюр, но capacity_in=100 — не должно превысить максимум
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=50, std_in=0, mean_out=0, std_out=0)
    atm.update_levels(24)
    assert atm.current_in <= atm.capacity_in
 
def test_update_levels_current_out_not_below_zero():
    # mean_out=50 за 24ч = 1200 снятий, но current_out не может уйти ниже 0
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=50, std_out=0)
    atm.update_levels(24)
    assert atm.current_out >= 0
 
def test_update_levels_zero_stats():
    # Если mean_in=0 и mean_out=0 — уровни не изменились
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=0, std_out=0)
    atm.update_levels(24)
    assert atm.current_in == 0
    assert atm.current_out == 100

def test_is_critical_yellow_warning():
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=3, std_in=0, mean_out=0, std_out=0)
    # Через 24 часа: pred_in = 0 + 3*24 = 72 (72% от 100)
    is_crit, reason = atm.is_critical(24)
    assert is_crit == True
    assert reason == "YELLOW"

def test_repr_returns_string():
    atm = Atm(1, 55.75, 37.62, 100, 200)
    result = repr(atm)
    assert isinstance(result, str)
    assert "Atm" in result
    assert "1" in result
