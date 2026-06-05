import json
import math
from flask import Flask, jsonify, render_template, request
from data_loader import load_atms
from db_connection import get_connection
from atm import Atm
from greedy_algorithm import nearest_neighbor_route
from clustering import cluster_atms
from two_opt import route_total_time

app = Flask(__name__)


def distance_km(atm1, atm2):
    R = 6371
    lat1, lon1 = math.radians(atm1.lat), math.radians(atm1.lon)
    lat2, lon2 = math.radians(atm2.lat), math.radians(atm2.lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c * 1.4


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map_day1')
def map_day1():
    return render_template('map_day1.html')


@app.route('/map_day2')
def map_day2():
    return render_template('map_day2.html')


@app.route('/map_day3')
def map_day3():
    return render_template('map_day3.html')


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


@app.route('/api/route', methods=['GET'])
def api_route():
    day = request.args.get('day', 1, type=int)

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

    # Получаем список обслуженных банкоматов из БД за предыдущие дни
    serviced_ids = set()
    if day > 1:
        conn = get_connection()
        try:
            cur = conn.cursor()
            for prev_day in range(1, day):
                cur.execute("SELECT stops FROM routes WHERE day = %s;", (prev_day,))
                rows = cur.fetchall()
                for row in rows:
                    stops = row[0]
                    if isinstance(stops, str):
                        stops = json.loads(stops)
                    if isinstance(stops, list):
                        for stop in stops:
                            if isinstance(stop, int):
                                serviced_ids.add(stop)
                            elif isinstance(stop, list) and len(stop) == 2:
                                # Это координаты, пропускаем
                                pass
            cur.close()
        except Exception:
            pass
        finally:
            if conn:
                conn.close()

    # Сбрасываем уровни обслуженным банкоматам
    for atm in atms:
        if atm.id in serviced_ids:
            atm.current_in = 0
            atm.current_out = atm.capacity_out

    # Обновляем уровни для текущего дня
    hours_passed = 24 * (day - 1)
    for atm in atms:
        atm.update_levels(hours_passed)

    red_count = sum(1 for atm in atms if atm.get_risk_level() == "RED")
    yellow_count = sum(1 for atm in atms if atm.get_risk_level() == "YELLOW")
    green_count = sum(1 for atm in atms if atm.get_risk_level() == "GREEN")
    critical_count = red_count + yellow_count

    if critical_count == 0:
        routes = []
        for car_id in range(1, 6):
            routes.append({"car": car_id, "stops": [], "total_atms": 0, "total_time": 0})
        return jsonify({
            "day": day, "routes": routes,
            "red": red_count, "yellow": yellow_count, "green": green_count,
            "critical": critical_count, "unserviced": 0, "serviced_before": len(serviced_ids)
        })

    critical_atms = [atm for atm in atms if atm.get_risk_level() in ("RED", "YELLOW")]
    priority_order = {"RED": 0, "YELLOW": 1, "GREEN": 2}
    sorted_critical = sorted(critical_atms, key=lambda a: priority_order.get(a.get_risk_level(), 2))

    routes = []
    chunk_size = len(sorted_critical) // 5
    remainder = len(sorted_critical) % 5
    start = 0

    for car_id in range(1, 6):
        extra = 1 if car_id <= remainder else 0
        end = start + chunk_size + extra
        group = sorted_critical[start:end]
        start = end

        if not group:
            routes.append({"car": car_id, "stops": [], "total_atms": 0, "total_time": 0})
            continue

        route = nearest_neighbor_route(group, use_graph=True)
        stops = [[atm.lat, atm.lon] for atm in route]

        try:
            total_time_sec = route_total_time(route)
            total_time = round(total_time_sec / 60)
        except Exception:
            total_time = len(route) * 15

        if total_time > 480:
            max_atms = 480 // 15
            route = route[:max_atms]
            stops = [[atm.lat, atm.lon] for atm in route]
            try:
                total_time_sec = route_total_time(route)
                total_time = round(total_time_sec / 60)
            except Exception:
                total_time = len(route) * 15

        routes.append({
            "car": car_id,
            "stops": stops,
            "total_atms": len(stops),
            "total_time": total_time
        })

    total_serviced = sum(r["total_atms"] for r in routes)
    unserviced = critical_count - total_serviced
       
    return jsonify({
        "day": day, "routes": routes,
        "red": red_count, "yellow": yellow_count, "green": green_count,
        "critical": critical_count, "unserviced": unserviced
    })

if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=5000)