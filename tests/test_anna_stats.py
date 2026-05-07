# Тесты для кода Ани (статистика и время)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import_route_utils():
    """Проверяет, что файл route_utils.py существует"""
    try:
        import route_utils
        assert hasattr(route_utils, 'check_work_time')
    except ImportError:
        assert False, "Файл route_utils.py не найден"

def test_import_stats():
    """Проверяет, что файл со статистикой существует"""
    try:
        import stats
        assert hasattr(stats, 'calculate_mean')
    except ImportError:
        assert False, "Файл stats.py не найден"

def test_import_dispersion():
    """Проверяет, что файл с дисперсией существует"""
    try:
        import dispersion
        assert hasattr(dispersion, 'calculate_dispersion')
    except ImportError:
        assert False, "Файл dispersion.py не найден"
