# Smart Log Analysis with Kafka 

## Problem Statement

- **Collect Logs**: Gather logs from different services in one place. This allows for centralized monitoring of application performance across various components.
- **Help Monitor Application Performance**: Track how well applications are running, making it easier to spot anomalies and performance issues in real-time.
- **Track Changes**: Record how the application's state changes over time, capturing important events that can help identify trends, errors, and performance metrics.
- **Easier Troubleshooting**: By examining historical logs and changes, the system helps developers and system administrators find and fix problems more efficiently.
- **Instant Analysis**: Set up a real-time processing pipeline that immediately analyzes incoming logs, leveraging AI models to interpret data and trigger actionable insights without delay.

## Requirements

### 1. **Logstash**: 8.17.1 or higher

### 2. **Kafka**: A running Kafka broker (localhost:9092 in this setup)

### 3. **Python 3.x**

### 4. **Java**: OpenJDK 17 or compatible (bundled with Logstash by default)

## Project Structure
smart_log_analysis/

* kafka/
  > producer.py
  
  > consumer.py

* ai_model/
  > train_model.py
  
  > model.py
  
  > saved_model/

* database/
  > db_config.py
  
  > db_init.py

* web/
  > app.py

* templates/
  > index.html
  
* static/
  > style.css

* js/
  > chart.js

## How to Run 



