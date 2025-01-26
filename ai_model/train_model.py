import pandas as pd
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

def parse_log_file(log_file_path):
    log_entries = []
    
    with open(log_file_path, 'r') as file:
        line_count = 0
        parsing_errors = 0
        for line in file:
            line_count += 1
            parsed_data = parse_log_line(line)
            if parsed_data:
                log_entries.append(parsed_data)
            else:
                parsing_errors += 1
    
    print(f"Total lines processed: {line_count}")
    print(f"Total parsing errors: {parsing_errors}")
    print(f"Total valid log entries: {len(log_entries)}")
    
    df = pd.DataFrame(log_entries, columns=['timestamp', 'service', 'status', 'message'])
    return df

def parse_log_line(log_line):
    log_pattern = r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+(?P<service>[\w\.\-]+(?:\[?\d*\]?)?)\s*(?P<message>.*)'
    match = re.match(log_pattern, log_line)
    
    if match:
        timestamp = match.group('timestamp')
        service = match.group('service')
        message = match.group('message')
        
        status = "Info"
        error_keywords = ['Error', 'fail', 'exception', 'critical', 'warning']
        if any(keyword in message.lower() for keyword in error_keywords):
            status = "Error"
        
        return timestamp, service, status, message
    return None

def extract_features(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%b %d %H:%M:%S')
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.weekday
    df['message_length'] = df['message'].apply(len)
    
    # Advanced anomaly detection features
    error_keywords = ['Error', 'failed', 'exception', 'critical', 'warning']
    df['error_keywords_count'] = df['message'].apply(
        lambda x: sum(x.lower().count(keyword) for keyword in error_keywords)
    )
    
    df['is_anomaly'] = (
        (df['error_keywords_count'] > 0) | 
        (df['status'] == 'Error') | 
        (df['message_length'] > 100)
    ).astype(int)
    
    return df

def train_model(log_file_path, model_path):
    print("Processing log file...")
    df = parse_log_file(log_file_path)
    
    if df.empty:
        print("No data found in the log file.")
        return
    
    print("Extracting features...")
    df_features = extract_features(df)
    
    X = df_features[['service', 'message', 'hour_of_day', 'day_of_week', 'message_length', 'error_keywords_count']]
    y = df_features['is_anomaly']
    
    print("Training model...")
    pipeline = Pipeline([
        ('preprocessor', ColumnTransformer([
            ('message_tfidf', TfidfVectorizer(max_features=1000), 'message'),
            ('service_onehot', OneHotEncoder(handle_unknown='ignore'), ['service'])
        ])),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline.fit(X_train, y_train)
    
    # Model evaluation
    y_pred = pipeline.predict(X_test)
    print("\nModel Performance:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved to {model_path}")

def main():
    log_file_path = "/Users/sumukha/Work/kafka_terra/Mac_2k.log"
    model_path = "ai_model/saved_model/log_model.pkl"
    train_model(log_file_path, model_path)

if __name__ == "__main__":
    main()