# Distributed Fraud Detection System

This project is a microservices ecosystem designed to detect insurance claims fraud in real-time. It leverages a decoupled architecture to separate high-frequency data ingestion from compute-heavy machine learning analysis.



## 🌟 Key Features
- **Real-time Ingestion:** FastAPI handles high-concurrency requests with low latency.
- **Event-Driven Analysis:** RabbitMQ acts as a buffer, ensuring no claim is lost even during high traffic spikes.
- **Predictive Scoring:** Random Forest Classifier trained on 1,000+ historical insurance claims.
- **Graph Link Analysis:** Neo4j maps relationships between policies and incidents to uncover hidden fraud rings.

---

## 🏗️ System Architecture & Data Flow

1. **API Layer (FastAPI):** Receives the JSON claim and pushes it to a RabbitMQ queue.
2. **Messaging Layer (RabbitMQ):** Manages the "claim_queue" asynchronously.
3. **Intelligence Layer (Worker.py):** Consumes messages, applies a pre-trained ML model, and generates a fraud score.
4. **Graph Persistence (Neo4j):** Stores the results as a relationship graph for visual analysis.

## 📊 Dataset Information
The model is trained using the **Insurance Claims Dataset** available on Kaggle.
- **Source:** [Kaggle - Insurance Claims Dataset](https://www.kaggle.com/datasets/mexwell/insurance-claims)
- **Content:** Includes 1,000 records of insurance claims with features like policy details, incident severity, and claim amounts.

---

## 🛠️ Project Structure
```text
.
├── app/
│   └── main.py              # FastAPI Ingestion API
├── scripts/
│   ├── train_model.py       # ML Model training script
│   ├── worker.py            # AI Prediction & Neo4j Worker
│   ├── fraud_model.pkl      # Saved Scikit-Learn model
│   ├── scaler.pkl           # Saved normalization scaler
│   └── model_columns.pkl    # Metadata for feature alignment
├── data/
│   └── insurance_claims.csv # Training dataset
├── docker-compose.yml       # Infrastructure (RabbitMQ & Neo4j)
├── requirements.txt         # Project dependencies
└── .gitignore               # Excludes venv and cache files
```

# 🚀 Setup & Installation
## 1. Infrastructure (Docker)
Ensure Docker is running, then spin up the backend services:
``` python
docker-compose up -d
```
Access RabbitMQ Management: http://localhost:15672 (guest/guest) Access Neo4j Browser: http://localhost:7474 (neo4j/password)

## 2. Environment Setup
``` python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Model Training
If you want to re-train the model from the CSV data:

``` python
python3 scripts/train_model.py
```
# 🏃 Running the Application
## Step 1: Start the AI Worker
In a new terminal:
``` python
python3 scripts/worker.py
```

## Step 2: Start the FastAPI Server
In another terminal:
``` python
python3 -m uvicorn app.main:app --reload
```
# 📡 API Documentation
## Endpoint: POST /analyze

``` python
{
  "policy_number": "POL-999",
  "months_as_customer": 120,
  "policy_deductable": 1000,
  "umbrella_limit": 0,
  "capital_gains": 50000,
  "capital_loss": 0,
  "incident_hour_of_the_day": 14,
  "number_of_vehicles_involved": 1,
  "bodily_injuries": 1,
  "witnesses": 2,
  "injury_claim": 5000,
  "property_claim": 10000,
  "vehicle_claim": 30000
}
```
## Success Response (200 OK):
``` python
{
  "status": "success",
  "message": "Claim POL-999 is being processed by AI"
}
```

# 📊 Analytics Deep-Dive
- **Model**: Random Forest Classifier (n_estimators=100)
- **Accuracy**: ~73.5% on test set.
- **Key Features** : incident_severity, injury_claim, vehicle_claim.

# 👤 Author
**Koustav Sarkar** MCA Student | NIT Raipur
