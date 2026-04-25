from server.database import get_db_connection

def test():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    print("Columns in users:")
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    test()
