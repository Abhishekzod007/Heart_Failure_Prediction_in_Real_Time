from kafka import KafkaProducer
import json
import time
import random

# Define Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Define the topic name
topic_name = 'heart_data'

# Function to generate random heart patient data
def generate_patient_data():
    return {
        "id": random.randint(1000, 9999),
        "age": random.randint(30, 80),
        "gender": random.choice([0, 1]),  # 0: Female, 1: Male
        "height": random.randint(140, 200),  # in cm
        "weight": random.randint(50, 120),  # in kg
        "ap_hi": random.randint(90, 180),  # Systolic BP
        "ap_lo": random.randint(60, 120),  # Diastolic BP
        "cholesterol": random.randint(1, 3),  # 1: Normal, 2: Above Normal, 3: High
        "gluc": random.randint(1, 3),  # 1: Normal, 2: Above Normal, 3: High
        "smoke": random.choice([0, 1]),
        "alco": random.choice([0, 1]),
        "active": random.choice([0, 1])
    }

# Produce messages continuously
while True:
    data = generate_patient_data()
    producer.send(topic_name, value=data)
    print(f"Sent: {data}")
    time.sleep(7)  # Adjust frequency of data generation
