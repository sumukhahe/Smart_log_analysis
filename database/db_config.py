import psycopg2

def check_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",       # Database server address
            database="logs_db",     # Database name
            user="sumukha",        # Database user
            password="newpassword" # Database password
        )
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_connection()
