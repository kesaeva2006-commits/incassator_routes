import os

def test_frontend_html():
    """Проверяет, что файл index.html существует и содержит нужный текст"""
    
    # Проверяем, что файл существует
    assert os.path.exists('templates/index.html'), "Файл templates/index.html не найден"
    
    # Читаем содержимое файла
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем заголовок страницы
    assert '<title>Инкассаторские маршруты - Москва</title>' in content, "Неверный заголовок страницы"
    
    # Проверяем текст на кнопке
    assert 'Построить маршрут' in content, "Кнопка 'Построить маршрут' не найдена"
    
    # Проверяем упоминание 5 машин
    assert '5 машин' in content, "Упоминание '5 машин' не найдено"
    
    # Проверяем предупреждение о критических банкоматах
    assert 'Критических банкоматов' in content, "Блок с критическими банкоматами не найден"
