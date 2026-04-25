from server.database import get_db_connection

def test():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Try an execute and fetch
    try:
        email = "test@example.com"
        cursor.execute("SELECT id, email, name, role, student_id, avatar_url, is_verified FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        print("Success:", user)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    test()
