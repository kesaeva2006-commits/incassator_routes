import sys
import os
from enum import Enum

import pytest

# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm


# ============================================================
# КОНСТАНТЫ СТАТУСОВ
# ============================================================

class AtmStatus(Enum):
    """Строковые статусы банкомата для использования в тестах."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    RED_IN_OVERFLOW = "RED_IN_OVERFLOW"
    RED_OUT_EMPTY = "RED_OUT_EMPTY"


# ============================================================
# ФИКСТУРЫ
# ============================================================

@pytest.fixture
def basic_atm():
    """Банкомат с базовыми параметрами для тестов без статистики."""
    return Atm(1, 55.75, 37.62, 100, 100)


@pytest.fixture
def stats_atm():
    """Банкомат со статистикой притока/оттока для тестов прогнозирования."""
    return Atm(1, 55.75, 37.62, 100, 100, mean_in=10, std_in=2, mean_out=15, std_out=3)


@pytest.fixture
def zero_stats_atm():
    """Банкомат с нулевой статистикой: нет движения купюр."""
    return Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=0, std_out=0)


# ============================================================
# ТЕСТЫ ДЛЯ КОНСТРУКТОРА И БАЗОВЫХ ПАРАМЕТРОВ
# ============================================================

def test_atm_creation(basic_atm):
    """Проверяет, что конструктор корректно сохраняет все переданные параметры."""
    assert basic_atm.id == 1
    assert basic_atm.lat == 55.75
    assert basic_atm.lon == 37.62
    assert basic_atm.capacity_in == 100
    assert basic_atm.capacity_out == 100


def test_atm_creation_with_stats(stats_atm):
    """Проверяет корректное сохранение параметров статистики при создании банкомата."""
    assert stats_atm.mean_in == 10
    assert stats_atm.std_in == 2
    assert stats_atm.mean_out == 15
    assert stats_atm.std_out == 3


def test_atm_initial_state(basic_atm):
    """Проверяет начальное состояние бункеров: приём пуст, выдача заполнена."""
    assert basic_atm.current_in == 0
    assert basic_atm.current_out == 100


def test_atm_invalid_capacity():
    """Проверяет, что ValueError поднимается при capacity_in = 0."""
    with pytest.raises(ValueError):
        Atm(1, 55.75, 37.62, 0, 100)


def test_repr_returns_string(basic_atm):
    """Проверяет, что __repr__ возвращает строку, содержащую имя класса и id."""
    result = repr(basic_atm)
    assert isinstance(result, str)
    assert "Atm" in result
    assert "1" in result


# ============================================================
# ТЕСТЫ ДЛЯ МЕТОДА needs_service
# ============================================================

def test_needs_service_true_when_in_full(basic_atm):
    """Проверяет, что банкомат требует обслуживания при полностью заполненном бункере приёма."""
    basic_atm.current_in = 100  # 100% заполнения — явное переполнение
    assert basic_atm.needs_service() is True


def test_needs_service_true_when_in_at_90_percent(basic_atm):
    """Проверяет срабатывание при достижении порога 90% заполнения бункера приёма."""
    basic_atm.current_in = 90  # граница срабатывания: бункер заполнен на 90%
    assert basic_atm.needs_service() is True


def test_needs_service_false_when_in_below_90(basic_atm):
    """Проверяет, что ниже порога 90% обслуживание не требуется."""
    basic_atm.current_in = 89  # на 1 единицу ниже порога срабатывания (90%)
    assert basic_atm.needs_service() is False


def test_needs_service_true_when_out_empty(basic_atm):
    """Проверяет, что банкомат требует обслуживания при полностью пустом бункере выдачи."""
    basic_atm.current_out = 0  # бункер выдачи пуст
    assert basic_atm.needs_service() is True


def test_needs_service_true_when_out_at_10_percent(basic_atm):
    """Проверяет срабатывание при достижении порога 10% остатка в бункере выдачи."""
    basic_atm.current_out = 10  # граница срабатывания: осталось 10% от capacity_out
    assert basic_atm.needs_service() is True


def test_needs_service_false_when_out_above_10(basic_atm):
    """Проверяет, что выше порога 10% обслуживание не требуется."""
    basic_atm.current_out = 11  # на 1 единицу выше порога срабатывания (10%)
    assert basic_atm.needs_service() is False


# ============================================================
# ТЕСТЫ ДЛЯ МЕТОДА predict_level_after_hours
# ============================================================

def test_predict_returns_floats(stats_atm):
    """Проверяет, что метод возвращает числовые значения для обоих бункеров."""
    pred_in, pred_out = stats_atm.predict_level_after_hours(24)
    assert isinstance(pred_in, (int, float))
    assert isinstance(pred_out, (int, float))


def test_predict_with_zero_stats(zero_stats_atm):
    """Проверяет прогноз при нулевой статистике: уровни не должны меняться."""
    pred_in, pred_out = zero_stats_atm.predict_level_after_hours(24)
    assert pred_in == 0
    assert pred_out == 100  # current_out = capacity_out = 100


# ============================================================
# ТЕСТЫ ДЛЯ МЕТОДА is_critical
# ============================================================

def test_is_critical_returns_tuple(stats_atm):
    """Проверяет, что метод возвращает кортеж (bool, str)."""
    is_crit, reason = stats_atm.is_critical(24)
    assert isinstance(is_crit, bool)
    assert isinstance(reason, str)


def test_is_critical_green_when_normal():
    """Проверяет статус GREEN при нормальных уровнях через 24 часа.

    mean_in=1, mean_out=1 => за 24ч приём=24%, выдача=76% — оба в норме.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=1, std_in=0, mean_out=1, std_out=0)
    is_crit, reason = atm.is_critical(24)
    assert is_crit is False
    assert reason == AtmStatus.GREEN.value


def test_is_critical_red_in_overflow():
    """Проверяет статус RED_IN_OVERFLOW при переполнении бункера приёма.

    mean_in=100 => за 24ч приём накапливает 2400 ед. при capacity=100 => переполнение.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=100, std_in=0, mean_out=0, std_out=0)
    is_crit, reason = atm.is_critical(24)
    assert is_crit is True
    assert reason == AtmStatus.RED_IN_OVERFLOW.value


def test_is_critical_red_out_empty():
    """Проверяет статус RED_OUT_EMPTY при опустошении бункера выдачи.

    mean_out=100 => за 24ч бункер выдачи расходует 2400 ед. при начальном запасе 100 => пусто.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=100, std_out=0)
    is_crit, reason = atm.is_critical(24)
    assert is_crit is True
    assert reason == AtmStatus.RED_OUT_EMPTY.value


def test_is_critical_yellow_warning():
    """Проверяет статус YELLOW при умеренном заполнении бункера приёма.

    mean_in=3, hours=24 => pred_in = 0 + 3*24 = 72 (72% от capacity=100) => порог YELLOW >70%.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=3, std_in=0, mean_out=0, std_out=0)
    is_crit, reason = atm.is_critical(24)
    assert is_crit is True
    assert reason == AtmStatus.YELLOW.value


# ============================================================
# ТЕСТЫ ДЛЯ МЕТОДА predict_inflow
# ============================================================
# Метод считает, сколько купюр накопится в бункере приёма через N часов.
# Формула: current_in + mean_in * hours + 2 * std_in * sqrt(hours)

def test_predict_inflow_returns_float():
    """Проверяет, что метод возвращает числовое значение."""
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=10, std_in=2, mean_out=0, std_out=0)
    result = atm.predict_inflow(24)
    assert isinstance(result, (int, float))


def test_predict_inflow_zero_stats(zero_stats_atm):
    """Проверяет, что при нулевой статистике бункер приёма остаётся пустым."""
    result = zero_stats_atm.predict_inflow(24)
    assert result == 0


def test_predict_inflow_correct_value():
    """Проверяет точность расчёта прогнозируемого притока.

    mean_in=2, std_in=0, hours=10 => 0 + 2*10 + 0 = 20.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=2, std_in=0, mean_out=0, std_out=0)
    result = atm.predict_inflow(10)
    assert result == 20


def test_predict_inflow_grows_with_time():
    """Проверяет, что прогноз притока увеличивается с ростом горизонта прогнозирования."""
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=5, std_in=0, mean_out=0, std_out=0)
    result_12 = atm.predict_inflow(12)
    result_24 = atm.predict_inflow(24)
    assert result_24 > result_12, "Прогноз приёма за 24ч должен быть больше, чем за 12ч"


def test_predict_inflow_with_nonzero_current():
    """Проверяет учёт текущего уровня бункера в прогнозе.

    current_in=30, mean_in=2, hours=10 => 30 + 2*10 = 50.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=2, std_in=0, mean_out=0, std_out=0)
    atm.current_in = 30
    result = atm.predict_inflow(10)
    assert result == 50


# ============================================================
# ТЕСТЫ ДЛЯ МЕТОДА predict_outflow
# ============================================================
# Метод считает, сколько денег останется в бункере выдачи через N часов.
# Формула: current_out - (mean_out * hours + 2 * std_out * sqrt(hours))

def test_predict_outflow_returns_float():
    """Проверяет, что метод возвращает числовое значение."""
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=5, std_out=1)
    result = atm.predict_outflow(24)
    assert isinstance(result, (int, float))


def test_predict_outflow_zero_stats(zero_stats_atm):
    """Проверяет, что при нулевой статистике бункер выдачи остаётся полным."""
    result = zero_stats_atm.predict_outflow(24)
    assert result == 100  # current_out = capacity_out = 100, расхода нет


def test_predict_outflow_correct_value():
    """Проверяет точность расчёта остатка в бункере выдачи.

    mean_out=3, std_out=0, hours=10 => 100 - 3*10 = 70.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=3, std_out=0)
    result = atm.predict_outflow(10)
    assert result == 70


def test_predict_outflow_decreases_with_time():
    """Проверяет, что остаток в бункере выдачи уменьшается с ростом горизонта прогнозирования."""
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=5, std_out=0)
    result_12 = atm.predict_outflow(12)
    result_24 = atm.predict_outflow(24)
    assert result_24 < result_12, "Прогноз остатка за 24ч должен быть меньше, чем за 12ч"


# ============================================================
# ТЕСТЫ ДЛЯ МЕТОДА get_risk_level
# ============================================================
# Метод возвращает уровень риска: "GREEN", "YELLOW" или "RED".
# RED    — бункер приёма >90% или выдача <10%
# YELLOW — приём >70% или выдача <30%
# GREEN  — всё в норме

def test_get_risk_level_returns_string():
    """Проверяет, что метод возвращает строковое значение."""
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=5, std_in=0, mean_out=5, std_out=0)
    result = atm.get_risk_level(24)
    assert isinstance(result, str)


def test_get_risk_level_green():
    """Проверяет уровень GREEN при нормальных прогнозируемых уровнях.

    mean_in=1, mean_out=1 => за 24ч приём=24%, выдача=76% — оба показателя в норме.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=1, std_in=0, mean_out=1, std_out=0)
    result = atm.get_risk_level(24)
    assert result == AtmStatus.GREEN.value


def test_get_risk_level_red_in_overflow():
    """Проверяет уровень RED при переполнении бункера приёма.

    mean_in=100 => за 24ч накапливается 2400 ед. при capacity=100 — критическое переполнение.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=100, std_in=0, mean_out=0, std_out=0)
    result = atm.get_risk_level(24)
    assert result == AtmStatus.RED.value


def test_get_risk_level_red_out_empty():
    """Проверяет уровень RED при полном опустошении бункера выдачи.

    mean_out=100 => за 24ч расходуется 2400 ед. при начальном запасе 100 — критически пусто.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=100, std_out=0)
    result = atm.get_risk_level(24)
    assert result == AtmStatus.RED.value


def test_get_risk_level_yellow():
    """Проверяет уровень YELLOW при умеренном заполнении бункера приёма.

    mean_in=3, hours=24 => pred_in = 3*24 = 72 (72% от capacity=100) — превышен порог YELLOW (>70%).
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=3, std_in=0, mean_out=0, std_out=0)
    result = atm.get_risk_level(24)
    assert result == AtmStatus.YELLOW.value


# ============================================================
# ТЕСТЫ ДЛЯ МЕТОДА update_levels
# ============================================================
# Метод обновляет реальные текущие уровни бункеров после прошедшего времени.
# В отличие от predict_* — изменяет атрибуты объекта (current_in и current_out).

def test_update_levels_increases_current_in():
    """Проверяет корректное увеличение бункера приёма после обновления уровней.

    mean_in=5, hours=10 => current_in = 0 + 5*10 = 50.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=5, std_in=0, mean_out=0, std_out=0)
    atm.update_levels(10)
    assert atm.current_in == 50


def test_update_levels_decreases_current_out():
    """Проверяет корректное уменьшение бункера выдачи после обновления уровней.

    mean_out=3, hours=10 => current_out = 100 - 3*10 = 70.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=3, std_out=0)
    atm.update_levels(10)
    assert atm.current_out == 70


def test_update_levels_current_in_not_exceed_capacity():
    """Проверяет, что current_in не превышает capacity_in после обновления уровней.

    mean_in=50, hours=24 => расчётный приток 1200 ед., но ограничен capacity_in=100.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=50, std_in=0, mean_out=0, std_out=0)
    atm.update_levels(24)
    assert atm.current_in <= atm.capacity_in, "current_in не должен превышать capacity_in"


def test_update_levels_current_out_not_below_zero():
    """Проверяет, что current_out не уходит ниже нуля после обновления уровней.

    mean_out=50, hours=24 => расчётный расход 1200 ед., но ограничен минимумом 0.
    """
    atm = Atm(1, 55.75, 37.62, 100, 100, mean_in=0, std_in=0, mean_out=50, std_out=0)
    atm.update_levels(24)
    assert atm.current_out >= 0, "current_out не должен опускаться ниже нуля"


def test_update_levels_zero_stats(zero_stats_atm):
    """Проверяет, что при нулевой статистике уровни бункеров не изменяются."""
    zero_stats_atm.update_levels(24)
    assert zero_stats_atm.current_in == 0
    assert zero_stats_atm.current_out == 100
