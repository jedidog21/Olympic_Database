import os
import sys

import psycopg
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()
conn_str = os.environ["DATABASE_URL"]

username, password, role = sys.argv[1], sys.argv[2], sys.argv[3]

with psycopg.connect(conn_str) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO app_user (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, generate_password_hash(password), role),
        )

print(f"Added {role} {username}")
