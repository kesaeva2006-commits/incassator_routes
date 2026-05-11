import os

# Тест 1: проверяет, что в ветке Ани есть файл atm.py
def test_atm_file_exists_in_anna_branch():
    assert os.path.exists('atm.py'), "Файл atm.py не найден (должен быть в ветке Ани)"

# Тест 2: проверяет, что в ветке Ани есть файл route_utils.py
def test_route_utils_exists_in_anna_branch():
    assert os.path.exists('route_utils.py'), "Файл route_utils.py не найден (должен быть в ветке Ани)"
