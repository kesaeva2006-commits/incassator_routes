from db_connection import get_connection

def create_tables():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS atms (
                id SERIAL PRIMARY KEY,
                lat DOUBLE PRECISION NOT NULL,
                lon DOUBLE PRECISION NOT NULL,
                capacity_in INT NOT NULL,
                capacity_out INT NOT NULL,
                mean_in FLOAT DEFAULT 0,
                std_in FLOAT DEFAULT 0,
                mean_out FLOAT DEFAULT 0,
                std_out FLOAT DEFAULT 0
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id SERIAL PRIMARY KEY,
                day INT NOT NULL,
                group_id INT NOT NULL,
                stops JSONB NOT NULL,
                total_time INT DEFAULT 0
            );
        """)

        conn.commit()
        print("Tables atms and routes created.")
        cur.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_tables()