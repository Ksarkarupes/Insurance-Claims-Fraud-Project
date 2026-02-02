import pika
import json
import joblib
import pandas as pd
import numpy as np
from neo4j import GraphDatabase
import os

# 1. Load the "Brain" and "Rules" (The files you generated earlier)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(file_name):
    return os.path.join(BASE_DIR, file_name)

# 1. Load the "Brain" and "Rules" using absolute paths
try:
    model = joblib.load(get_path('fraud_model.pkl'))
    scaler = joblib.load(get_path('scaler.pkl'))
    model_columns = joblib.load(get_path('model_columns.pkl'))
    print("AI Assets loaded successfully from:", BASE_DIR)
except Exception as e:
    print(f"Error loading AI assets: {e}")
    exit()

# 2. Neo4j Connection Setup
uri = "bolt://localhost:7687"
neo4j_driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

def save_to_neo4j(claim_id, result, incident_type):
    with neo4j_driver.session() as session:
        session.run("""
            MERGE (c:Claim {id: $id})
            SET c.fraud_prediction = $res
            MERGE (i:Incident {type: $itype})
            MERGE (c)-[:TYPE_OF]->(i)
        """, id=claim_id, res=result, itype=incident_type)

# 3. Processing Logic
def process_claim(ch, method, properties, body):
    try:
        # Convert JSON string from RabbitMQ to Python Dict
        data = json.loads(body)
        print(f"[*] Processing Claim: {data.get('policy_number', 'Unknown')}")

        # Convert to DataFrame for the model
        df = pd.DataFrame([data])

        # Feature Engineering: One-Hot Encoding
        # This creates the same columns the model expects (e.g., policy_csl_250/500)
        df_encoded = pd.get_dummies(df)

        # Ensure all columns from training are present (add missing as 0)
        for col in model_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        
        # Reorder columns to match the training schema exactly
        df_final = df_encoded[model_columns]

        # Scaling (Only the numerical columns)
        cols_to_scale = ['months_as_customer', 'policy_deductable', 'umbrella_limit',
                         'capital-gains', 'capital-loss', 'incident_hour_of_the_day',
                         'number_of_vehicles_involved', 'bodily_injuries', 'witnesses', 
                         'injury_claim', 'property_claim', 'vehicle_claim']
        
        # We check if these columns exist in our incoming data before scaling
        available_cols = [c for c in cols_to_scale if c in df_final.columns]
        df_final[available_cols] = scaler.transform(df_final[available_cols])

        # PREDICTION
        prediction = model.predict(df_final)[0]
        result_text = "FRAUD" if prediction == 'Y' else "LEGIT"

        # Update Neo4j
        save_to_neo4j(data.get('policy_number'), result_text, data.get('incident_type', 'Unknown'))

        print(f"[✔] Result for {data.get('policy_number')}: {result_text}")

    except Exception as e:
        print(f"[✘] Error processing message: {e}")

# 4. RabbitMQ Connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='claim_queue', durable=True)
channel.basic_consume(queue='claim_queue', on_message_callback=process_claim, auto_ack=True)

print(' [*] Waiting for claims. To exit press CTRL+C')
channel.start_consuming()