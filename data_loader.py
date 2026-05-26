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
            
            cap_in = row[3]
            cap_out = row[4]
            cur_in = row[9]
            cur_out = row[10]

            if cur_out == 0:
                cur_out = cap_out

            in_ratio = cur_in / cap_in if cap_in > 0 else 0
            out_ratio = 1 - (cur_out / cap_out) if cap_out > 0 else 0

            if in_ratio > 0.9 or out_ratio > 0.9:
                status = "red"
            elif in_ratio > 0.7 or out_ratio > 0.7:
                status = "yellow"
            else:
                status = "green"

            atms_list.append({
                "id": row[0],
                "lat": row[1],
                "lon": row[2],
                "capacity_in": cap_in,
                "capacity_out": cap_out,
                "mean_in": row[5],
                "std_in": row[6],
                "mean_out": row[7],
                "std_out": row[8],
                "current_in_level": cur_in,
                "current_out_level": cur_out,
                "status": status
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