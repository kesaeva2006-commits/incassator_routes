import csv
import io
import json
import logging
from flask import Flask, jsonify, render_template, request, Response
from data_loader import load_atms
from db_connection import get_connection
from atm import Atm
from greedy_algorithm import nearest_neighbor_route
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map_day<int:day>')
def map_day(day):
    return render_template(f'map_day{day}.html')

@app.route('/atms', methods=['GET'])
def get_all_atms():
    atms = load_atms()
    return jsonify(atms)

@app.route('/route', methods=['POST'])
def save_route():
    data = request.get_json()
    day = data.get('day')
    group_id = data.get('group_id')
    stops = data.get('stops')
    total_time = data.get('total_time', 0)

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO routes (day, group_id, stops, total_time)
               VALUES (%s, %s, %s, %s)""",
            (day, group_id, json.dumps(stops), total_time)
        )
        conn.commit()
        cur.close()
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/routes', methods=['GET'])
def get_routes():
    day = request.args.get('day', type=int)
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM routes WHERE day = %s ORDER BY group_id;", (day,))
        rows = cur.fetchall()
        routes_list = []
        for row in rows:
            routes_list.append({
                "id": row[0],
                "day": row[1],
                "group_id": row[2],
                "stops": row[3],
                "total_time": row[4]
            })
        return jsonify(routes_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/atms/update', methods=['POST'])
def update_atms():
    data = request.get_json()
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        for atm_data in data:
            cur.execute(
                """UPDATE atms
                   SET current_in_level = %s, current_out_level = %s
                   WHERE id = %s""",
                (atm_data['current_in_level'], atm_data['current_out_level'], atm_data['id'])
            )
        conn.commit()
        cur.close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/atms/stats', methods=['GET'])
def api_atms_stats():
    from generator import generate_atms
    atms = generate_atms(1000, seed=42)

    for atm in atms:
        atm.update_levels(48)

    counts = {"RED": 0, "YELLOW": 0, "GREEN": 0}
    for atm in atms:
        level = atm.get_risk_level(hours_ahead=24)
        counts[level] = counts.get(level, 0) + 1

    return jsonify({
        "total": len(atms),
        "red": counts["RED"],
        "yellow": counts["YELLOW"],
        "green": counts["GREEN"],
    })

@app.route('/api/route', methods=['GET'])
def api_route():
    day = request.args.get('day', 1, type=int)
    group_id = request.args.get('group_id', type=int)
    atms_dicts = load_atms()
    atms = []
    for d in atms_dicts:
        atm = Atm(
            atm_id=d['id'],
            lat=d['lat'],
            lon=d['lon'],
            capacity_in=d['capacity_in'],
            capacity_out=d['capacity_out'],
            mean_in=d['mean_in'],
            std_in=d['std_in'],
            mean_out=d['mean_out'],
            std_out=d['std_out']
        )
        atms.append(atm)

    route = nearest_neighbor_route(atms, use_graph=False)
    stops = [[atm.lat, atm.lon] for atm in route]
    
    result = {
        "day": day,
        "stops": stops,
        "car": group_id if group_id else 1,
        "total_atms": len(stops)
    }

    return jsonify(result)

# Добавь этот эндпоинт в app.py (после существующих маршрутов)

@app.route('/api/routes/all', methods=['GET'])
def api_routes_all():
    """
    Возвращает маршруты всех машин за указанный день из routes.json.
    Параметр: ?day=2
    """
    import os
    day = request.args.get('day', 2, type=int)

    json_path = os.path.join(os.path.dirname(__file__), 'routes.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_routes = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "routes.json не найден. Сначала запустите generate_atms_json.py"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    day_routes = [r for r in all_routes if r.get('day') == day]

    if not day_routes:
        return jsonify([])

    result = []
    for r in day_routes:
        stops = r.get('stops', [])
        result.append({
            "car": r.get('car'),
            "day": r.get('day'),
            "stops": len(stops),          # количество банкоматов
            "critical_count": r.get('critical_count', 0),
            "total_time": r.get('total_time', 0.0),
        })

    return jsonify(result)


@app.route('/api/routes/compare', methods=['GET'])
def api_routes_compare():
    import os
    json_path = os.path.join(os.path.dirname(__file__), 'routes.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_routes = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "routes.json не найден"}), 404

    days = sorted({r.get('day') for r in all_routes if r.get('day')})
    result = []
    for day in days:
        day_routes = [r for r in all_routes if r.get('day') == day]
        total_atms = sum(len(r.get('stops', [])) for r in day_routes)
        total_critical = sum(r.get('critical_count', 0) for r in day_routes)
        times = [r.get('total_time', 0) for r in day_routes if r.get('total_time')]
        avg_time = sum(times) / len(times) if times else 0
        result.append({
            "day": day,
            "cars": len(day_routes),
            "atms": total_atms,
            "critical": total_critical,
            "avg_time": round(avg_time, 1),
        })

    return jsonify(result)


@app.route('/api/routes/export', methods=['GET'])
def api_routes_export():
    import os
    from generator import generate_atms
    day = request.args.get('day', 2, type=int)

    json_path = os.path.join(os.path.dirname(__file__), 'routes.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_routes = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "routes.json не найден"}), 404

    day_routes = [r for r in all_routes if r.get('day') == day]

    atms = generate_atms(1000, seed=42)
    for atm in atms:
        atm.update_levels(48)
    atm_by_coord = {(round(a.lat, 6), round(a.lon, 6)): a for a in atms}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['day', 'car', 'stop_order', 'atm_id', 'lat', 'lon', 'status'])

    for route in day_routes:
        for i, stop in enumerate(route.get('stops', []), 1):
            key = (round(stop[0], 6), round(stop[1], 6))
            atm = atm_by_coord.get(key)
            writer.writerow([
                day,
                route.get('car'),
                i,
                atm.id if atm else '',
                stop[0],
                stop[1],
                atm.get_risk_level(24) if atm else 'UNKNOWN',
            ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=routes_day{day}.csv'}
    )


@app.route('/api/routes/detail', methods=['GET'])
def api_routes_detail():
    import os
    from generator import generate_atms
    day = request.args.get('day', 2, type=int)
    car = request.args.get('car', type=int)

    json_path = os.path.join(os.path.dirname(__file__), 'routes.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            all_routes = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "routes.json не найден"}), 404

    route = next((r for r in all_routes if r.get('day') == day and r.get('car') == car), None)
    if not route:
        return jsonify({"error": "Маршрут не найден"}), 404

    atms = generate_atms(1000, seed=42)
    for atm in atms:
        atm.update_levels(48)
    atm_by_coord = {(round(a.lat, 6), round(a.lon, 6)): a for a in atms}

    stops_detail = []
    for i, stop in enumerate(route.get('stops', []), 1):
        key = (round(stop[0], 6), round(stop[1], 6))
        atm = atm_by_coord.get(key)
        stops_detail.append({
            "order": i,
            "lat": stop[0],
            "lon": stop[1],
            "atm_id": atm.id if atm else None,
            "status": atm.get_risk_level(24) if atm else "UNKNOWN",
        })

    return jsonify(stops_detail)


def update_atm_levels_job():
    """Обновляет уровни банкоматов в БД каждые 24 часа."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, capacity_in, capacity_out, mean_in, std_in, mean_out, std_out, current_in_level, current_out_level FROM atms ORDER BY id;")
        rows = cur.fetchall()
        for row in rows:
            atm_id, cap_in, cap_out, mean_in, std_in, mean_out, std_out, cur_in, cur_out = row
            atm = Atm(atm_id=atm_id, lat=0, lon=0, capacity_in=cap_in, capacity_out=cap_out,
                      mean_in=mean_in, std_in=std_in, mean_out=mean_out, std_out=std_out)
            atm.current_in = cur_in or 0
            atm.current_out = cur_out if cur_out is not None else cap_out
            atm.update_levels(24)
            cur.execute(
                "UPDATE atms SET current_in_level = %s, current_out_level = %s WHERE id = %s",
                (int(atm.current_in), int(atm.current_out), atm_id)
            )
        conn.commit()
        cur.close()
        app.logger.info("ATM levels updated (%d records)", len(rows))
    except Exception as e:
        app.logger.warning("ATM update job failed: %s", e)
    finally:
        if conn:
            conn.close()


scheduler = BackgroundScheduler()
scheduler.add_job(update_atm_levels_job, 'interval', hours=24, id='atm_levels_update')
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
