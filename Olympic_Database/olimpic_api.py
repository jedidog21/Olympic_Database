import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn_str = os.environ.get("DATABASE_URL")


with psycopg.connect(conn_str) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Athletes;")
        print(cur.fetchall())
