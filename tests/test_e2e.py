import sys
import os
import time
import json
from unittest.mock import patch, MagicMock

# Добавляем корневую папку проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import app

# ==============================================================
# E2E ТЕСТЫ: от HTTP-запроса до HTTP-ответа
# Проверяем всю цепочку: клиент → Flask → обработчик → ответ
# БД и load_atms мокируются чтобы тесты работали без PostgreSQL в CI
# ==============================================================

@pytest.fixture
def client():
    """Тестовый клиент Flask — имитирует браузер/HTTP-клиент"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_e2e_index_returns_200(client):
    """Главная страница должна отвечать 200 OK за < 30 секунд"""
    start = time.time()
    response = client.get('/')
    elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 30

def test_e2e_get_atms_returns_200(client):
    """GET /atms должен вернуть 200 OK. БД мокируется"""
    mock_atms = [{"id": i, "lat": 55.75, "lon": 37.62} for i in range(10)]
    with patch('app.load_atms', return_value=mock_atms):
        start = time.time()
        response = client.get('/atms')
        elapsed = time.time() - start
    assert response.status_code == 200
    assert elapsed < 30

def test_e2e_get_atms_response_time(client):
    """
    ГЛАВНЫЙ E2E ТЕСТ ВРЕМЕНИ: GET /atms с 1000 банкоматами
    должен вернуть ответ быстрее 30 секунд
    """
    mock_atms = [{"id": i, "lat": 55.55 + i*0.001, "lon": 37.30 + i*0.001} for i in range(1000)]
    with patch('app.load_atms', return_value=mock_atms):
        start = time.time()
        response = client.get('/atms')
        elapsed = time.time() - start
    assert response.status_code == 200
    assert len(response.get_json()) == 1000
    assert elapsed < 30, f"GET /atms занял {elapsed:.2f}с — превышен лимит 30с!"
    print(f"\n GET /atms (1000 банкоматов) ответил за {elapsed:.3f}с")

def test_e2e_post_route_returns_201(client):
    """POST /route должен сохранять маршрут и возвращать 201. БД мокируется"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    payload = {"day": 1, "group_id": 1, "stops": [1, 2, 3], "total_time": 120}
    with patch('app.get_connection', return_value=mock_conn):
        response = client.post('/route', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 201
    assert response.get_json()['status'] == 'ok'

def test_e2e_get_routes_returns_200(client):
    """GET /routes?day=1 должен вернуть список маршрутов за день. БД мокируется"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1, 1, 1, json.dumps([1, 2, 3]), 120)]
    with patch('app.get_connection', return_value=mock_conn):
        response = client.get('/routes?day=1')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
