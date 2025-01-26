import json
import logging
from confluent_kafka import Consumer, KafkaError
import joblib
import psycopg2

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# LogAnalyzer class for analyzing logs and storing results in the database
class LogAnalyzer:
    def __init__(self, model_path, db_config):
        # Load ML model for anomaly detection
        self.model = joblib.load(model_path)
        
        # Set up PostgreSQL connection
        self.conn = psycopg2.connect(**db_config)
        self.cursor = self.conn.cursor()

    # Analyze log entry and predict whether it's normal or an anomaly
    def analyze_log(self, log_entry):
        try:
            # Ensure the necessary keys exist in the log entry
            if 'service' not in log_entry or 'message' not in log_entry:
                logger.error(f"Log entry missing 'service' or 'message': {log_entry}")
                return 'Unknown'

            error_keywords = ['Error', 'critical', 'fatal', 'exception', 'failed']

            # Create feature set (simulating the training process)
            features = {
                'service': log_entry['service'],
                'message': log_entry['message'],
                'status': log_entry.get('status', 'Info')
            }

            # Simple rule-based check for manual anomaly detection
            manual_anomaly = (
                any(keyword in log_entry['message'].lower() for keyword in error_keywords) or
                log_entry.get('status') == 'Error' or
                len(log_entry['message']) > 100
            )

            # Use the machine learning model for further anomaly verification
            try:
                ml_prediction = self.model.predict([features])[0]
            except Exception as ml_error:
                logger.warning(f"ML prediction failed: {ml_error}")
                ml_prediction = manual_anomaly

            # Return 'Anomaly' if either manual check or ML prediction indicates an issue
            return 'Anomaly' if manual_anomaly or ml_prediction else 'Normal'

        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return 'Unknown'

    # Store the analyzed log entry into the database
    def store_log(self, log_entry, analysis_result):
        try:
            # SQL query to insert the log entry and its analysis result into the database
            insert_query = """
            INSERT INTO logs (timestamp, service, status, message, analysis_result)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (
                log_entry.get('timestamp', ''),
                log_entry['service'], 
                log_entry.get('status', 'Info'),
                log_entry['message'],
                analysis_result
            ))
            self.conn.commit()

        except Exception as e:
            logger.error(f"Error storing log: {e}")
            self.conn.rollback()

# Main function that sets up the Kafka consumer and processes logs
def main():
    consumer_conf = {
        'bootstrap.servers': 'localhost:9092',  # Kafka server address
        'group.id': 'log-analysis-group',        # Consumer group ID
        'auto.offset.reset': 'earliest'          # Start from the earliest message
    }

    # Database configuration for PostgreSQL
    db_config = {
        'database': 'logs_db',
        'user': 'sumukha',
        'password': 'newpassword',
        'host': 'localhost',
        'port': '5432'
    }

    # Path to the pre-trained ML model
    MODEL_PATH = 'ai_model/saved_model/log_model.pkl'
    KAFKA_TOPIC = 'logs'  # Kafka topic to consume messages from

    # Initialize the Kafka consumer
    consumer = Consumer(consumer_conf)
    consumer.subscribe([KAFKA_TOPIC])

    # Initialize the log analyzer with model and database configuration
    log_analyzer = LogAnalyzer(MODEL_PATH, db_config)

    try:
        while True:
            # Poll Kafka for new messages
            msg = consumer.poll(1.0)

            # Skip if no message
            if msg is None:
                continue

            # Handle Kafka errors
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info('Reached end of partition')
                else:
                    logger.error(f'Error: {msg.error()}')
                continue

            # Parse the message value
            log_entry = json.loads(msg.value().decode('utf-8'))
            logger.info(f"Received log entry: {log_entry}")  # Log the incoming message for debugging

            # Analyze the log entry (Normal or Anomaly)
            analysis_result = log_analyzer.analyze_log(log_entry)

            # Store the analyzed log entry in the database
            log_analyzer.store_log(log_entry, analysis_result)

    except KeyboardInterrupt:
        logger.info('Stopping consumer...')
    finally:
        # Ensure proper closing of the consumer
        consumer.close()

# Run the main function if this script is executed
if __name__ == "__main__":
    main()
