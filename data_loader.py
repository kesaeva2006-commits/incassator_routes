# -*- coding: utf-8 -*-
from db_connection import get_connection
from atm import Atm
from generator import generate_atms


def save_atms(atms):
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM atms;")
        for atm in atms:
            cur.execute(
                """INSERT INTO atms
                   (lat, lon, capacity_in, capacity_out, mean_in, std_in, mean_out, std_out)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    atm.lat,
                    atm.lon,
                    atm.capacity_in,
                    atm.capacity_out,
                    atm.mean_in,
                    atm.std_in,
                    atm.mean_out,
                    atm.std_out
                )
            )
        conn.commit()
        print(f"Loaded {len(atms)} ATMs.")
        cur.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


def load_atms():
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM atms ORDER BY id;")
        rows = cur.fetchall()
        atms_list = []
        for row in rows:
            atms_list.append({
                "id": row[0],
                "lat": row[1],
                "lon": row[2],
                "capacity_in": row[3],
                "capacity_out": row[4],
                "mean_in": row[5],
                "std_in": row[6],
                "mean_out": row[7],
                "std_out": row[8]
            })
        return atms_list
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    atms = generate_atms(1000)
    save_atms(atms)
    loaded = load_atms()
    print(f"Check: loaded {len(loaded)} records from DB.")