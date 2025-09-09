from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, IntegerType
import joblib
import pandas as pd
import shap
import time
import os
import csv

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkHeartDataConsumer") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
    .getOrCreate()

# Kafka configurations
KAFKA_TOPIC = "heart_data"
KAFKA_BROKER = "localhost:9092"

# Load model and SHAP explainer
model = joblib.load("heart_failure_xgb_model.pkl")
explainer = joblib.load("shap_explainer.pkl")

# Load the features used for training to maintain order
with open("features_used.txt", "r") as f:
    feature_names = [line.strip() for line in f]

# Define schema for incoming JSON data
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("age", IntegerType(), True),
    StructField("gender", IntegerType(), True),
    StructField("height", IntegerType(), True),
    StructField("weight", IntegerType(), True),
    StructField("ap_hi", IntegerType(), True),
    StructField("ap_lo", IntegerType(), True),
    StructField("cholesterol", IntegerType(), True),
    StructField("gluc", IntegerType(), True),
    StructField("smoke", IntegerType(), True),
    StructField("alco", IntegerType(), True),
    StructField("active", IntegerType(), True)
])

# Read data from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# Convert Kafka message value to JSON DataFrame
df = df.selectExpr("CAST(value AS STRING)") \
       .select(from_json(col("value"), schema).alias("data")) \
       .select("data.*")

# Prediction and SHAP explanation function
import subprocess



# Prediction and SHAP explanation function
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Configuration
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "Cpc5A0mA195DIbVclGNKwbGqagl02xeBsuzoU1nLuEWJUFtvAEB2dEXoudcaES5NYyrMgEcaidzpXxm7I1leWA=="  # Replace with your actual token
INFLUX_ORG = "ABVIIITM"        # Replace with your actual org
INFLUX_BUCKET = "RealtimeData"        # Replace with your bucket name

# Initialize InfluxDB client once
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def predict(batch_df, batch_id):
    if batch_df.count() > 0:
        start_time = time.time()

        pandas_df = batch_df.toPandas()

        # Extract user ID and drop from features if present
        if "id" in pandas_df.columns:
            user_ids = pandas_df["id"].tolist()
            pandas_df = pandas_df.drop(columns=["id"])
        else:
            user_ids = ["Unknown"] * len(pandas_df)

        pandas_df = pandas_df[feature_names]

        # Make prediction and compute SHAP values
        predictions = model.predict(pandas_df)
        shap_values = explainer.shap_values(pandas_df)

        end_time = time.time()
        print(f"\n📦 Batch ID: {batch_id} | ⏱ Time taken: {end_time - start_time:.4f} sec")

        # For each row: print and write to InfluxDB
        for i, (uid, pred, shap_row) in enumerate(zip(user_ids, predictions, shap_values)):
            # Top 3 positive & negative SHAP features
            top_positive = sorted(zip(feature_names, shap_row), key=lambda x: x[1], reverse=True)[:3]
            top_negative = sorted(zip(feature_names, shap_row), key=lambda x: x[1])[:3]

            print(f"\n🧑‍⚕️ User ID: {uid}")
            print(f"   ➤ Prediction: {'High Risk' if pred == 1 else 'Low Risk'}")
            print(f"   🔍 Top 3 Positive SHAP contributions:")
            for fname, value in top_positive:
                print(f"      - {fname}: {value:+.4f}")
            print(f"   🔍 Top 3 Negative SHAP contributions:")
            for fname, value in top_negative:
                print(f"      - {fname}: {value:+.4f}")

            # Create and write InfluxDB point
            point = (
                Point("heart_prediction")
                .tag("user_id", str(uid))
                .tag("batch_id", str(batch_id))
                .field("prediction", int(pred))
                .field("top_pos_1", round(top_positive[0][1], 4))
                .field("top_pos_1_name", top_positive[0][0])
                .field("top_pos_2", round(top_positive[1][1], 4))
                .field("top_pos_2_name", top_positive[1][0])
                .field("top_pos_3", round(top_positive[2][1], 4))
                .field("top_pos_3_name", top_positive[2][0])
                .field("top_neg_1", round(top_negative[0][1], 4))
                .field("top_neg_1_name", top_negative[0][0])
                .field("top_neg_2", round(top_negative[1][1], 4))
                .field("top_neg_2_name", top_negative[1][0])
                .field("top_neg_3", round(top_negative[2][1], 4))
                .field("top_neg_3_name", top_negative[2][0])
                .field("time_taken", round(end_time - start_time, 4))
                .time(time.time_ns(), WritePrecision.NS)
            )

            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

        print("✅ All predictions and SHAP explanations written to InfluxDB.")

# Apply prediction and explanation function
df.writeStream \
    .foreachBatch(predict) \
    .start() \
    .awaitTermination()
