import joblib
import pandas as pd

model = joblib.load("ai_model/saved_model/log_model.pkl")

def analyze_log(log):
    df = pd.DataFrame([log])
    df = pd.get_dummies(df)
    return model.predict(df)[0]
