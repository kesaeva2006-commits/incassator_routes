import os

def test_frontend():
    # Ищем файл в любом месте репозитория
    found = False
    for root, dirs, files in os.walk('.'):
        if 'index.html' in files:
            found = True
            break
    assert found, "index.html не найден в репозитории"
