import json
from flask import Flask, jsonify, render_template, request
from data_loader import load_atms
from db_connection import get_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)