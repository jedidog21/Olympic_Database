import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn_str = os.environ.get("DATABASE_URL")


with psycopg.connect(conn_str) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT e.Team FROM Events e LEFT JOIN Athletes a ON a.ID = e.ID WHERE a.Name = 'A Dijiang';")
        print(cur.fetchall())

        cur.execute("SELECT e.Games FROM Events e LEFT JOIN Athletes a ON a.ID = e.ID WHERE a.Name = 'A Dijiang';")
        print(cur.fetchall())
        cur.execute("SELECT DISTINCT Games FROM Events WHERE NOC = 'CPV';")
        print(cur.fetchall())
        cur.execute("SELECT DISTINCT Games FROM Events WHERE Team = 'Cape Verde';")
        print(cur.fetchall())

        cur.execute("SELECT COUNT(*) FROM Events WHERE NOC = 'CAN' AND Medal != 'NA';")
        print(cur.fetchall())

        cur.execute("SELECT Height, Weight FROM Athletes WHERE Name = 'A Dijiang';")
        print(cur.fetchall())

        cur.execute("SELECT a.Sex, COUNT(a.*) FROM Athletes a LEFT JOIN Events e ON e.ID = a.ID WHERE e.Team = 'Cape Verde' GROUP BY a.Sex;")
        print(cur.fetchall())
