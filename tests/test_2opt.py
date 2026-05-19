import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock  # инструменты для подмены функций в тестах
from atm import Atm
from two_opt import two_opt  # импортируем тестируемую функцию

def make_atms(n):
    """Создаёт список из n тестовых банкоматов с разными координатами"""
    # Каждый банкомат чуть дальше предыдущего на 0.01 градуса
    return [Atm(i, 55.75 + i * 0.01, 37.62 + i * 0.01, 100, 100) for i in range(n)]

def mock_travel_time(atm1, atm2, G, atm_to_node):
    """Заглушка вместо реального расчёта времени по карте Москвы"""
    # Вместо загрузки графа дорог считаем простое расстояние по координатам
    return abs(atm1.lat - atm2.lat) + abs(atm1.lon - atm2.lon)

# @patch — подменяем тяжёлые функции на заглушки чтобы не скачивать карту Москвы
@patch('two_opt.load_moscow_graph')  # подменяем загрузку графа
@patch('two_opt.match_atms_to_nodes')  # подменяем привязку к узлам графа
@patch('two_opt.travel_time_between', side_effect=mock_travel_time)  # подменяем расчёт времени
def test_two_opt_returns_list(mock_tt, mock_match, mock_graph):
    """Проверяет что 2-opt возвращает список"""
    mock_graph.return_value = MagicMock()  # граф — пустой объект-заглушка
    mock_match.return_value = {}  # привязка банкоматов — пустой словарь
    atms = make_atms(5)
    result = two_opt(atms)
    assert isinstance(result, list)  # результат должен быть списком

@patch('two_opt.load_moscow_graph')
@patch('two_opt.match_atms_to_nodes')
@patch('two_opt.travel_time_between', side_effect=mock_travel_time)
def test_two_opt_same_length(mock_tt, mock_match, mock_graph):
    """Проверяет что 2-opt не теряет и не добавляет банкоматы"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = make_atms(6)
    result = two_opt(atms)
    # Количество банкоматов должно остаться прежним
    assert len(result) == len(atms)

@patch('two_opt.load_moscow_graph')
@patch('two_opt.match_atms_to_nodes')
@patch('two_opt.travel_time_between', side_effect=mock_travel_time)
def test_two_opt_contains_all_atms(mock_tt, mock_match, mock_graph):
    """Проверяет что все банкоматы остались в маршруте после оптимизации"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = make_atms(5)
    result = two_opt(atms)
    # Каждый банкомат из исходного списка должен быть в результате
    for atm in atms:
        assert atm in result

@patch('two_opt.load_moscow_graph')
@patch('two_opt.match_atms_to_nodes')
@patch('two_opt.travel_time_between', side_effect=mock_travel_time)
def test_two_opt_short_route_unchanged(mock_tt, mock_match, mock_graph):
    """Маршрут из менее чем 4 банкоматов возвращается без изменений"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    atms = make_atms(3)
    result = two_opt(atms)
    # Короткий маршрут не оптимизируется — возвращается как есть
    assert result == atms

@patch('two_opt.load_moscow_graph')
@patch('two_opt.match_atms_to_nodes')
@patch('two_opt.travel_time_between', side_effect=mock_travel_time)
def test_two_opt_empty_list(mock_tt, mock_match, mock_graph):
    """Пустой маршрут возвращается без изменений"""
    mock_graph.return_value = MagicMock()
    mock_match.return_value = {}
    result = two_opt([])
    # Пустой список должен вернуться пустым
    assert result == []
