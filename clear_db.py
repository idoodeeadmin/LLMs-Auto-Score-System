from server.database import get_db_connection, init_db

def clear_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables_to_drop = [
        "email_verifications",
        "password_resets",
        "submission_answers",
        "submissions",
        "questions",
        "exams",
        "enrollments",
        "rooms",
        "users"
    ]
    
    # Disable foreign key checks temporarily to make dropping easier
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped table {table}")
        except Exception as e:
            print(f"Error dropping {table}: {e}")
            
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    conn.close()
    
    print("Database cleared. Reinitializing...")
    init_db()
    print("Database successfully reinitialized and is now empty.")

if __name__ == "__main__":
    clear_database()
