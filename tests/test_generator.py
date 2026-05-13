import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm import Atm
from generator import generate_test_atms

# Алиас (для краткости)
generate_atms = generate_test_atms

# ТЕСТЫ ДЛЯ ФУНКЦИИ generate_atms

def test_generate_atms_returns_list():
    atms = generate_atms(10)
    assert isinstance(atms, list)

def test_generate_atms_returns_correct_number():
    atms = generate_atms(10)
    assert len(atms) == 10
    
    atms = generate_atms(5)
    assert len(atms) == 5
    
    atms = generate_atms(0)
    assert len(atms) == 0

def test_generate_atms_returns_atm_objects():
    atms = generate_atms(10)
    for atm in atms:
        assert isinstance(atm, Atm)

def test_generate_atms_returns_unique_ids():
    atms = generate_atms(10)
    ids = [atm.id for atm in atms]
    # Проверяем, что все ID уникальны
    assert len(set(ids)) == len(ids)

def test_generate_atms_seed_consistency():
    # При одинаковом seed результаты должны совпадать
    atms1 = generate_test_atms(5, seed=42)
    atms2 = generate_test_atms(5, seed=42)
    
    assert len(atms1) == len(atms2)
    for i in range(len(atms1)):
        assert atms1[i].lat == atms2[i].lat
        assert atms1[i].lon == atms2[i].lon
        assert atms1[i].capacity_in == atms2[i].capacity_in
        assert atms1[i].capacity_out == atms2[i].capacity_out

def test_generate_atms_different_seeds_produce_different_results():
    atms1 = generate_test_atms(5, seed=42)
    atms2 = generate_test_atms(5, seed=100)
    
    # Хотя бы одно значение должно отличаться
    is_different = False
    for i in range(len(atms1)):
        if (atms1[i].lat != atms2[i].lat or 
            atms1[i].lon != atms2[i].lon or
            atms1[i].capacity_in != atms2[i].capacity_in or
            atms1[i].capacity_out != atms2[i].capacity_out):
            is_different = True
            break
    assert is_different == True

def test_generate_atms_coordinates_in_range():
    atms = generate_atms(100)
    for atm in atms:
        assert 55.60 <= atm.lat <= 55.85
        assert 37.40 <= atm.lon <= 37.75

def test_generate_atms_capacities_in_range():
    atms = generate_atms(100)
    for atm in atms:
        assert 10000 <= atm.capacity_in <= 25000
        assert 12000 <= atm.capacity_out <= 20000

def test_generate_atms_default_count():
    atms = generate_test_atms()  # без параметров
    assert len(atms) == 10
