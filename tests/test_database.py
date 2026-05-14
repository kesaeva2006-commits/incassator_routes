import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Подменяем psycopg2 на sqlite3 для тестов
import psycopg2
from unittest.mock import patch

from atm import Atm
from data_loader import save_atms, load_atms

# Создаём тестовую таблицу (как в реальной БД)
def create_test_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS atms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL,
            lon REAL,
            capacity_in INTEGER,
            capacity_out INTEGER,
            mean_in REAL,
            std_in REAL,
            mean_out REAL,
            std_out REAL
        )
    """)
    conn.commit()

# Подменяем get_connection на SQLite
def mock_get_connection():
    conn = sqlite3.connect(':memory:')  # БД в памяти (не сохраняется)
    create_test_table(conn)
    return conn

@patch('db_connection.get_connection', side_effect=mock_get_connection)
def test_save_and_load_atms(mock_conn):
    # Создаём тестовые банкоматы
    atms = [
        Atm(1, 55.75, 37.62, 100, 100),
        Atm(2, 55.76, 37.63, 200, 200)
    ]
    
    # Сохраняем
    save_atms(atms)
    
    # Загружаем
    loaded = load_atms()
    
    # Проверяем
    assert len(loaded) == len(atms)
    for i, atm_data in enumerate(loaded):
        assert atm_data['lat'] == atms[i].lat
        assert atm_data['lon'] == atms[i].lon
