import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock  # инструменты для подмены реальных функций на заглушки
from atm import Atm
from data_loader import save_atms, load_atms  # импортируем тестируемые функции

def make_atms(n):
    """Создаёт список тестовых банкоматов"""
    # Каждый банкомат чуть дальше предыдущего на 0.01 градуса
    return [Atm(i, 55.75 + i * 0.01, 37.62 + i * 0.01, 100, 100,
                mean_in=10, std_in=1, mean_out=5, std_out=1) for i in range(n)]

# @patch подменяет get_connection на заглушку — реальная PostgreSQL не нужна
@patch('data_loader.get_connection')
def test_save_atms_calls_insert(mock_conn):
    """Проверяет что save_atms вызывает INSERT для каждого банкомата"""
    # Создаём заглушки для соединения и курсора БД
    mock_cursor = MagicMock()  # имитирует курсор (выполняет запросы)
    mock_connection = MagicMock()  # имитирует соединение с БД
    mock_connection.cursor.return_value = mock_cursor  # курсор возвращается из соединения
    mock_conn.return_value = mock_connection  # get_connection() вернёт нашу заглушку

    atms = make_atms(3)
    save_atms(atms)

    # Проверяем что execute вызывался 4 раза: 1 DELETE + 3 INSERT
    assert mock_cursor.execute.call_count == 4
    # Проверяем что commit был вызван — изменения сохранены
    mock_connection.commit.assert_called_once()

@patch('data_loader.get_connection')
def test_save_atms_calls_delete_first(mock_conn):
    """Проверяет что save_atms сначала удаляет старые записи"""
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_conn.return_value = mock_connection

    atms = make_atms(2)
    save_atms(atms)

    # Берём первый вызов execute и проверяем что это DELETE
    first_call = mock_cursor.execute.call_args_list[0]
    assert "DELETE" in first_call[0][0]  # первый аргумент первого вызова содержит DELETE

@patch('data_loader.get_connection')
def test_load_atms_returns_list(mock_conn):
    """Проверяет что load_atms возвращает список"""
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_conn.return_value = mock_connection

    # Имитируем что в БД есть 2 записи — возвращаем список кортежей как настоящая БД
    mock_cursor.fetchall.return_value = [
        (1, 55.75, 37.62, 100, 100, 10.0, 1.0, 5.0, 1.0),
        (2, 55.76, 37.63, 100, 100, 10.0, 1.0, 5.0, 1.0),
    ]

    result = load_atms()
    assert isinstance(result, list)  # результат должен быть списком
    assert len(result) == 2  # должно быть 2 записи

@patch('data_loader.get_connection')
def test_load_atms_returns_correct_fields(mock_conn):
    """Проверяет что load_atms возвращает правильные поля"""
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_conn.return_value = mock_connection

    # Одна запись с конкретными значениями для проверки
    mock_cursor.fetchall.return_value = [
        (1, 55.75, 37.62, 100, 200, 10.0, 1.0, 5.0, 1.0),
    ]

    result = load_atms()
    # Проверяем что все поля правильно распарсились из кортежа БД
    assert result[0]['lat'] == 55.75        # широта
    assert result[0]['lon'] == 37.62        # долгота
    assert result[0]['capacity_in'] == 100  # ёмкость бункера приёма
    assert result[0]['capacity_out'] == 200 # ёмкость бункера выдачи

@patch('data_loader.get_connection')
def test_load_atms_empty_db(mock_conn):
    """Проверяет что при пустой БД возвращается пустой список"""
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_conn.return_value = mock_connection

    # Имитируем пустую БД — fetchall возвращает пустой список
    mock_cursor.fetchall.return_value = []

    result = load_atms()
    assert result == []  # должен вернуться пустой список
