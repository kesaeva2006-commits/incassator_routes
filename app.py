import json
from flask import Flask, jsonify, render_template, request
from data_loader import load_atms
from db_connection import get_connection
from atm import Atm
from greedy_algorithm import nearest_neighbor_route

app = Flask(__name__)

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



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)