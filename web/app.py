from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# Connect to PostgreSQL database
conn = psycopg2.connect(
    database="logs_db",
    user="sumukha",
    password="newpassword", 
    host="localhost",
    port="5432"
)
cur = conn.cursor()

@app.route('/')
def index():
    # Get search query from URL
    search_query = request.args.get('search', '')

    # Fetch logs based on search query
    cur.execute("SELECT * FROM logs WHERE message LIKE %s", ('%' + search_query + '%',))
    logs = cur.fetchall()

    # Fetch counts for "Normal" and "Anomaly" logs
    cur.execute("SELECT COUNT(*) FROM logs WHERE analysis_result = 'Normal'")
    normal_count = cur.fetchone()[0]
    print("Normal Count:", normal_count)

    cur.execute("SELECT COUNT(*) FROM logs WHERE analysis_result = 'Anomaly'")
    anomaly_count = cur.fetchone()[0]
    print("Anomaly Count:", anomaly_count)

    return render_template('index.html', 
                           logs=logs, 
                           normal_count=normal_count, 
                           anomaly_count=anomaly_count)

@app.route('/stats')
def stats():
    # Query for basic statistics (Anomaly and Normal logs)
    cur.execute("SELECT COUNT(*) FROM logs WHERE analysis_result = 'Anomaly'")
    anomaly_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM logs WHERE analysis_result = 'Normal'")
    normal_count = cur.fetchone()[0]

    return render_template('stats.html', 
                           anomaly_count=anomaly_count, 
                           normal_count=normal_count)

if __name__ == '__main__':
    app.run(debug=True)