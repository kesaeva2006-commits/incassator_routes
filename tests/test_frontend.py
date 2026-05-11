import os

# Тест проверяет, что файл index.html существует в папке templates
def test_html_exists():
    html_path = os.path.join('templates', 'index.html')
    assert os.path.exists(html_path)
