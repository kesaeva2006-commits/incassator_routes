import sys
import os
 
# Добавляем корневую папку проекта в путь поиска модулей
# Чтобы Python мог найти priority_route.py, atm.py, generator.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from atm import Atm
from generator import generate_atms
from priority_route import sort_by_priority, build_priority_route, print_priority_summary
 
 
# ==============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# Создают банкоматы с нужным уровнем риска для тестов
# ==============================================================
 
def make_atm(atm_id, mean_in=0, std_in=0, mean_out=0, std_out=0):
    """Базовый банкомат с заданной статистикой"""
    return Atm(atm_id, 55.75, 37.62, 100, 100,
               mean_in=mean_in, std_in=std_in,
               mean_out=mean_out, std_out=std_out)
 
def make_red_atm(atm_id):
    """Банкомат с RED риском: mean_in=100 → за 24ч бункер приёма переполнится"""
    return make_atm(atm_id, mean_in=100)
 
def make_green_atm(atm_id):
    """Банкомат с GREEN риском: небольшой поток, всё в норме"""
    return make_atm(atm_id, mean_in=1, mean_out=1)
 
def make_yellow_atm(atm_id):
    """Банкомат с YELLOW риском: mean_in=3 → за 24ч приём >70%"""
    return make_atm(atm_id, mean_in=3)
 
 
# ==============================================================
# ТЕСТЫ ДЛЯ sort_by_priority
# Функция сортирует банкоматы по уровню риска: RED → YELLOW → GREEN
# ==============================================================
 
def test_sort_by_priority_returns_list():
    """Проверяет что функция возвращает список"""
    atms = [make_green_atm(1), make_red_atm(2), make_yellow_atm(3)]
    assert isinstance(sort_by_priority(atms), list)
 
def test_sort_by_priority_red_first():
    """Банкомат с RED риском должен быть первым в отсортированном списке"""
    result = sort_by_priority([make_green_atm(1), make_yellow_atm(2), make_red_atm(3)])
    assert result[0].get_risk_level() == "RED"
 
def test_sort_by_priority_green_last():
    """Банкомат с GREEN риском должен быть последним"""
    result = sort_by_priority([make_green_atm(1), make_yellow_atm(2), make_red_atm(3)])
    assert result[-1].get_risk_level() == "GREEN"
 
def test_sort_by_priority_preserves_count():
    """После сортировки количество банкоматов не должно измениться"""
    atms = [make_green_atm(i) for i in range(5)]
    assert len(sort_by_priority(atms)) == 5
 
def test_sort_by_priority_empty():
    """Пустой список должен вернуться пустым"""
    assert sort_by_priority([]) == []
 
 
# ==============================================================
# ТЕСТЫ ДЛЯ build_priority_route
# Функция строит маршрут с приоритетом: сначала RED, потом YELLOW, GREEN
# ==============================================================
 
def test_build_priority_route_returns_list():
    """Проверяет что функция возвращает список"""
    atms = generate_atms(10)
    assert isinstance(build_priority_route(atms), list)
 
def test_build_priority_route_contains_all_atms():
    """Все банкоматы должны попасть в маршрут — никто не потеряется"""
    atms = generate_atms(10)
    result = build_priority_route(atms)
    assert len(result) == len(atms)
    for atm in atms:
        assert atm in result
 
def test_build_priority_route_single_atm():
    """Маршрут из одного банкомата возвращается как есть"""
    atm = make_green_atm(1)
    assert build_priority_route([atm]) == [atm]
 
def test_build_priority_route_empty():
    """Пустой список возвращается без изменений"""
    assert build_priority_route([]) == []
 
 
# ==============================================================
# ТЕСТЫ ДЛЯ print_priority_summary
# Функция выводит в консоль сводку по уровням риска банкоматов
# ==============================================================
 
def test_print_priority_summary_runs(capsys):
    """Проверяет что функция выводит все три уровня риска"""
    atms = [make_red_atm(1), make_yellow_atm(2), make_green_atm(3)]
    print_priority_summary(atms)
    # capsys перехватывает вывод в консоль
    out = capsys.readouterr().out
    assert "RED" in out
    assert "YELLOW" in out
    assert "GREEN" in out
