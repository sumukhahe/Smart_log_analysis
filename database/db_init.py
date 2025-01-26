import psycopg2

def create_table():
    try:
        # Establish the connection
        conn = psycopg2.connect(
            host="localhost",       # Database server address
            database="logs_db",     # Database name
            user="sumukha",        # Database user
            password="newpassword" # Database password
        )
        cur = conn.cursor()

        # SQL query to create the logs table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            service TEXT,
            status TEXT,
            message TEXT,
            analysis_result TEXT
        );
        """

        # Execute the query
        cur.execute(create_table_query)
        
        # Commit the transaction
        conn.commit()
        
        print("Table 'logs' created successfully.")
        
        # Close the cursor and connection
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_table()
