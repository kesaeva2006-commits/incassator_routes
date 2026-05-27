# Маршруты инкассаторов

Система автоматического построения оптимальных маршрутов инкассации банкоматов по Москве. Поддерживает 1000 банкоматов, 5 кластеров, планирование на 3 дня с учётом приоритетов.

## Команда

| Роль | Участник |
|------|----------|
| Product Owner | Балаян Светлана |
| Scrum Master | Морозова Анастасия |
| Алгоритмист 1 | Хачатрян Луиза |
| Алгоритмист 2 | Никольская Анна |
| Backend | Рахматулина Лилия |
| Frontend | Голубинская Вероника |
| DevOps | Кесаева Ангелина |

## Как запустить

### Через Docker (рекомендуется)

```bash
docker-compose up --build
```

После запуска приложение доступно по адресу: http://localhost:5000

### Без Docker

```bash
git clone https://github.com/kesaeva2006-commits/incassator_routes.git
cd incassator_routes
pip install -r requirements.txt
python generate_atms_json.py
python app.py
```

## Функциональность

- **1000 банкоматов** — генерация и хранение данных о банкоматах Москвы
- **5 кластеров** — автоматическое разбиение банкоматов на 5 групп по географии (KMeans)
- **3 дня** — планирование маршрутов на 3 рабочих дня
- **Приоритеты** — банкоматы с критическим уровнем (RED/YELLOW/GREEN) обслуживаются первыми
- **Реальные дороги** — маршруты строятся по дорожной сети Москвы (OSMnx)

## Технологии

| Технология | Назначение |
|------------|------------|
| Python 3.12 | Основной язык |
| Flask | Веб-сервер и API |
| PostgreSQL | База данных маршрутов |
| Folium | Визуализация карт |
| OSMnx | Граф дорог Москвы |
| scikit-learn | KMeans кластеризация |
| Docker | Контейнеризация |
| GitHub Actions | CI/CD |

## Тестирование

```bash
pytest tests/ -v
pytest tests/ -v --cov=. --cov-report=term-missing
pytest tests/test_performance.py -v -s
pytest tests/test_e2e.py -v -s
```

## Требования

- Python 3.12
- PostgreSQL 13+
- Docker и Docker Compose

## Ссылка на доску задач

https://ru.yougile.com/team/82202708000f/Project#PRO-120
