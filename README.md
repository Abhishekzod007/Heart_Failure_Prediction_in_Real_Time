# 💓 Real-Time Heart Failure Prediction and Alert System

A **real-time, distributed heart failure prediction pipeline** built using **Apache Kafka, Apache Spark Streaming, and XGBoost**, capable of processing live patient vitals and triggering proactive alerts for high-risk cases.

---

## 📌 Overview
This project processes live patient health data in a **scalable and fault-tolerant** manner using **Apache Kafka** for ingestion, **Apache Spark Streaming** for distributed real-time processing, and a **tuned XGBoost model** for prediction.  
It integrates with **InfluxDB** and **Grafana** for real-time visualization and analytics.

---

## 🚀 Features
- **Real-time streaming** of JSON-based patient vitals from Kafka producers.
- **Scalable processing** with Spark Streaming in micro-batches.
- **Accurate ML predictions** using a tuned XGBoost model.
- **Real-time analytics** with InfluxDB and Grafana dashboards.
- **Proactive alert system** for high-risk predictions.
- **Fault-tolerant pipeline** for robust performance in real-world conditions.

---

## 🛠 Tech Stack
**Languages & Frameworks**
- Python 3.12  
- XGBoost  
- Pandas, NumPy, Scikit-learn  

**Big Data & Streaming**
- Apache Kafka  
- Apache Spark 3.5 (Streaming)  

**Databases & Visualization**
- InfluxDB  
- Grafana  

---

## 📂 Project Structure
```plaintext
📁 project-root/
 ├── data/                 # Datasets (UCI & CVD)
 ├── model/                # Saved XGBoost model
 ├── kafka_producer.py     # Sends real-time patient vitals to Kafka
 ├── spark_consumer.py     # Reads stream from Kafka & predicts
 ├── requirements.txt      # Python dependencies
 ├── README.md             # Documentation
