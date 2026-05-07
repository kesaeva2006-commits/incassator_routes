from flask import Flask, jsonify

app = Flask(__name__)

MOCK_ATMS = [
    {"id": 1, "lat": 55.751, "lon": 37.618, "capacity_in": 5000, "capacity_out": 10000},
    {"id": 2, "lat": 55.755, "lon": 37.617, "capacity_in": 4500, "capacity_out": 9000},
    {"id": 3, "lat": 55.760, "lon": 37.620, "capacity_in": 6000, "capacity_out": 8000},
]

@app.route('/atms', methods=['GET'])
def get_all_atms():
    return jsonify(MOCK_ATMS)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
