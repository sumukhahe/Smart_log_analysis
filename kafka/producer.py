import os
import json
import time
import re
from confluent_kafka import Producer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kafka configuration
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker address
}

# Create Kafka Producer
producer = Producer(conf)

def delivery_report(err, msg):
    """
    Callback function for message delivery report
    """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def parse_log_line(log_line):
    """
    Parse a single log line into components
    
    Args:
        log_line (str): Raw log line
    
    Returns:
        tuple: (service, status, message, timestamp) or (None, None, None, None)
    """
    log_pattern = r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+(?P<service>[\w\.\-]+(?:\[?\d*\]?)?)\s*(?P<message>.*)'
    match = re.match(log_pattern, log_line)
    
    if match:
        timestamp = match.group('timestamp')
        service = match.group('service')
        message = match.group('message')
        
        # Assign status based on message content
        status = "Info"
        if "Error" in message.lower() or "failed" in message.lower():
            status = "Error"
        elif "warning" in message.lower():
            status = "Warning"
        
        return service, status, message, timestamp
    
    return None, None, None, None

def send_log_to_kafka(service, status, message, timestamp):
    """
    Send log entry to Kafka topic
    
    Args:
        service (str): Service name
        status (str): Log status
        message (str): Log message
        timestamp (str): Log timestamp
    """
    log_entry = {
        'service': service,
        'status': status,
        'message': message,
        'timestamp': timestamp
    }
    
    try:
        # Produce message to Kafka topic
        producer.produce(
            topic='logs', 
            key=service.encode('utf-8'), 
            value=json.dumps(log_entry).encode('utf-8'), 
            callback=delivery_report
        )
        producer.poll(0)  # Trigger delivery callbacks
    except Exception as e:
        logger.error(f"Error sending log to Kafka: {e}")

def tail_log_file(log_file_path):
    """
    Continuously read and process new log entries
    
    Args:
        log_file_path (str): Path to log file
    """
    try:
        with open(log_file_path, 'r') as log_file:
            # Move to end of file
            log_file.seek(0, 2)
            
            while True:
                line = log_file.readline()
                if not line:
                    time.sleep(0.1)  # Wait for new logs
                    continue
                
                # Parse and send log
                service, status, message, timestamp = parse_log_line(line.strip())
                if service:
                    send_log_to_kafka(service, status, message, timestamp)
    
    except FileNotFoundError:
        logger.error(f"Log file not found: {log_file_path}")
    except KeyboardInterrupt:
        logger.info("Stopping log producer...")
    finally:
        # Close producer connection
        producer.flush()

def main():
    LOG_FILE_PATH = "/Users/sumukha/Work/kafka_terra/Mac_2k.log"
    tail_log_file(LOG_FILE_PATH)

if __name__ == '__main__':
    main()