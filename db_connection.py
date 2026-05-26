import os
import psycopg2

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:11lr00@localhost:5432/incassator_db'
)

def get_connection():
    return psycopg2.connect(DATABASE_URL)