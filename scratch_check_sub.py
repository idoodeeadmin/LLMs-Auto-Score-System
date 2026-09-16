import pymysql, json, os, sys
from dotenv import load_dotenv
load_dotenv()
from server.database import get_db_connection

conn = get_db_connection()
c = conn.cursor()
c.execute("SELECT * FROM submission_answers WHERE submission_id = 330004")
rows = c.fetchall()
with open("scratch/sub_330004.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2, default=str)
print("Saved to scratch/sub_330004.json")
conn.close()
