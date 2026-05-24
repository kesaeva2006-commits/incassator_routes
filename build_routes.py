"""
build_routes.py — сборщик маршрутов.

Берёт банкоматы из atms.json, прогоняет их через планировщик на 3 дня
(plan_multi_day) и сохраняет результат в routes.json в формате, который
читает generate_map.py:

    [
      {"day": 1, "car": 1, "stops": [[lat, lon], ...]},
      {"day": 1, "car": 2, "stops": [...]},
      ...
      {"day": 3, "car": 5, "stops": [...]}
    ]

Запускается автоматически в GitHub Actions — НЕ нужно запускать локально.
"""

import json
import os
from atm import Atm
from multi_day_planner import plan_multi_day

# Сколько дней планируем
DAYS = 3
# Путь к входным данным и результату
ATMS_FILE = 'atms.json'
ROUTES_FILE = 'routes.json'


def load_atms_from_json(path):
    """Читает atms.json и превращает каждую запись в объект Atm."""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    atms = []
    for item in data:
        atm = Atm(
            atm_id=item['id'],
            lat=item['lat'],
            lon=item['lon'],
            capacity_in=item['capacity_in'],
            capacity_out=item['capacity_out'],
            mean_in=item.get('mean_in', 0),
            std_in=item.get('std_in', 0),
            mean_out=item.get('mean_out', 0),
            std_out=item.get('std_out', 0),
        )
        atms.append(atm)
    return atms


def plan_to_routes_json(plan):
    """
    Превращает результат plan_multi_day (словарь по дням, где маршрут — список
    объектов Atm) в плоский список словарей для routes.json.
    """
    result = []
    for day in sorted(plan.keys()):
        routes = plan[day]['routes']  # список из 5 маршрутов (по машинам)
        for car_index, route in enumerate(routes, start=1):
            stops = [[atm.lat, atm.lon] for atm in route]
            result.append({
                'day': day,
                'car': car_index,
                'stops': stops,
            })
    return result


def main():
    print(f"Читаю банкоматы из {ATMS_FILE} ...")
    atms = load_atms_from_json(ATMS_FILE)
    print(f"Загружено банкоматов: {len(atms)}")

    print(f"Строю маршруты на {DAYS} дня ...")
    plan = plan_multi_day(atms, days=DAYS)

    routes_data = plan_to_routes_json(plan)

    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(routes_data, f, ensure_ascii=False, indent=2)

    # Короткая сводка
    print(f"\nГотово. Сохранено в {ROUTES_FILE}: {len(routes_data)} маршрутов")
    for block in routes_data:
        print(f"  День {block['day']}, машина {block['car']}: {len(block['stops'])} банкоматов")


if __name__ == '__main__':
    main()
