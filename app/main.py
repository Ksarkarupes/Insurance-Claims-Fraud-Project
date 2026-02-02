from fastapi import FastAPI
import pika
import json
from pydantic import BaseModel

app = FastAPI()

# 1. Define the Data Structure (The same fields you gave me)
class Claim(BaseModel):
    policy_number: str
    months_as_customer: int
    policy_deductable: int
    umbrella_limit: int
    capital_gains: int
    capital_loss: int
    incident_hour_of_the_day: int
    number_of_vehicles_involved: int
    bodily_injuries: int
    witnesses: int
    injury_claim: float
    property_claim: float
    vehicle_claim: float
    # You can add the other string fields here too

# 2. Setup RabbitMQ Connection
def send_to_queue(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='claim_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='claim_queue',
        body=json.dumps(data)
    )
    connection.close()

# 3. Create the Endpoint
@app.post("/analyze")
async def analyze_claim(claim: Claim):
    # Convert Pydantic model to dictionary
    claim_dict = claim.dict()
    
    # Send to RabbitMQ
    send_to_queue(claim_dict)
    
    return {"status": "success", "message": f"Claim {claim.policy_number} is being processed by AI"}