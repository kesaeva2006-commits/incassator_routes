import pytest
import random
from atm import Atm
from generator import generate_atms


class TestGenerateAtms:
    """Тесты для генерации банкоматов"""
    
    def test_default_count(self):
        """Проверка генерации 10 банкоматов по умолчанию"""
        atms = generate_atms()
        assert len(atms) == 10
        assert all(isinstance(atm, Atm) for atm in atms)
    
    def test_custom_count(self):
        """Проверка генерации произвольного количества"""
        atms = generate_atms(count=50, seed=42)
        assert len(atms) == 50
    
    def test_seed_reproducibility(self):
        """Проверка, что одинаковый seed дает одинаковые результаты"""
        atms1 = generate_atms(count=5, seed=42)
        atms2 = generate_atms(count=5, seed=42)
        
        for atm1, atm2 in zip(atms1, atms2):
            assert atm1.atm_id == atm2.atm_id
            assert atm1.lat == atm2.lat
            assert atm1.lon == atm2.lon
            assert atm1.capacity_in == atm2.capacity_in
            assert atm1.capacity_out == atm2.capacity_out
    
    def test_unique_ids(self):
        """Проверка уникальности ID банкоматов"""
        atms = generate_atms(count=100, seed=42)
        ids = [atm.atm_id for atm in atms]
        
        assert len(ids) == len(set(ids))
        assert min(ids) == 1
        assert max(ids) == 100
    
    def test_coordinates_within_moscow_bounds(self):
        """Проверка, что координаты в пределах Москвы"""
        atms = generate_atms(count=100, seed=42)
        
        LAT_MIN, LAT_MAX = 55.55, 55.95
        LON_MIN, LON_MAX = 37.30, 37.95
        
        for atm in atms:
            assert LAT_MIN <= atm.lat <= LAT_MAX
            assert LON_MIN <= atm.lon <= LON_MAX
    
    def test_capacity_ranges(self):
        """Проверка диапазонов вместимости"""
        atms = generate_atms(count=100, seed=42)
        
        for atm in atms:
            assert 8000 <= atm.capacity_in <= 30000
            assert 10000 <= atm.capacity_out <= 25000
    
    def test_statistics_initialized_to_zero(self):
        """Проверка, что статистика инициализируется нулями"""
        atms = generate_atms(count=10, seed=42)
        
        for atm in atms:
            assert atm.mean_in == 0
            assert atm.std_in == 0
            assert atm.mean_out == 0
            assert atm.std_out == 0
    
    def test_zero_count(self):
        """Проверка генерации 0 банкоматов"""
        atms = generate_atms(count=0, seed=42)
        assert len(atms) == 0
        assert isinstance(atms, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
