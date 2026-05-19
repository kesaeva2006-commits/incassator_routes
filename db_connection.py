import psycopg2

DB_CONFIG = {
    'dbname': 'incassator_db',
    'user': 'postgres',
    'password': '11lr00',
    'host': 'localhost',
    'port': 5432
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)
