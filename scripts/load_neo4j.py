import pandas as pd
from neo4j import GraphDatabase

# Connection details for the Docker container we started
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

def load_data():
    # Load your refined dataset
    df = pd.read_csv('../data/refined_dataset.csv')
    
    with driver.session() as session:
        # Clear existing data so you can run it multiple times
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create Graph nodes and relationships
        for index, row in df.head(100).iterrows(): # Loading 100 for speed tonight
            session.run("""
                MERGE (p:Policy {id: $policy_id})
                SET p.fraud = $fraud, p.amount = $amount
                MERGE (i:Incident {type: $incident_type})
                MERGE (p)-[:OCCURRED_AS]->(i)
                """, 
                policy_id=str(row['policy_number']),
                fraud=row['fraud_reported'],
                amount=row['total_claim_amount'],
                incident_type=row['incident_type']
            )
    print("Graph Data Loaded into Neo4j Successfully!")

if __name__ == "__main__":
    load_data()
    driver.close()