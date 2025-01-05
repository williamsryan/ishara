#!/usr/bin/env python3

import os
import sys

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import psycopg2
import redis
from confluent_kafka.admin import AdminClient, NewTopic
from elasticsearch import Elasticsearch
from src.utils.config import POSTGRES, REDIS, KAFKA, ELASTICSEARCH

def setup_postgres():
    """Set up the Postgres database schema using schema.sql."""
    try:
        print("[Postgres] Connecting to the database...")
        conn = psycopg2.connect(**POSTGRES)
        conn.autocommit = True  # Disable transaction block for DROP DATABASE
        cursor = conn.cursor()

        # Load schema.sql and execute it
        schema_path = os.path.join(project_root, "database/schema.sql")
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        cursor.execute(schema_sql)
        print("[Postgres] Schema setup complete.")

    except Exception as e:
        print(f"[Postgres] Error setting up schema: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def setup_redis():
    """Set up Redis with initial keys."""
    try:
        print("[Redis] Connecting to Redis...")
        r = redis.Redis(**REDIS)

        # Add test session key
        test_key = "session:example"
        test_value = {
            "user_email": "user@example.com",
            "configuration": {"selected_tickers": ["AAPL", "TSLA"]}
        }
        r.set(test_key, str(test_value), ex=3600)  # Expires in 1 hour
        print("[Redis] Added test session key.")

    except Exception as e:
        print(f"[Redis] Error setting up Redis: {e}")

def setup_kafka():
    """Set up Kafka topics."""
    try:
        print("[Kafka] Connecting to Kafka...")
        admin_client = AdminClient({"bootstrap.servers": KAFKA["broker"]})

        # Define topics
        topics = ["market_data_stream", "analysis_results_stream"]
        existing_topics = admin_client.list_topics().topics.keys()

        # Create only topics that don't exist
        new_topics = [
            NewTopic(topic, num_partitions=1, replication_factor=1)
            for topic in topics if topic not in existing_topics
        ]

        if new_topics:
            admin_client.create_topics(new_topics)
            print(f"[Kafka] Topics created: {topics}")
        else:
            print("[Kafka] Topics already exist.")

    except Exception as e:
        print(f"[Kafka] Error setting up Kafka: {e}")

def setup_elasticsearch():
    """Set up Elasticsearch indices."""
    try:
        print("[Elasticsearch] Connecting to Elasticsearch...")
        es = Elasticsearch(
            [ELASTICSEARCH["host"]],
            basic_auth=ELASTICSEARCH["http_auth"]
        )

        # Create indices for market data and analysis results
        market_data_index = {
            "mappings": {
                "properties": {
                    "symbol": {"type": "keyword"},
                    "datetime": {"type": "date"},
                    "open": {"type": "float"},
                    "high": {"type": "float"},
                    "low": {"type": "float"},
                    "close": {"type": "float"},
                    "volume": {"type": "long"}
                }
            }
        }
        es.options(ignore_status=400).indices.create(index="market_data", body=market_data_index)

        analysis_results_index = {
            "mappings": {
                "properties": {
                    "symbol": {"type": "keyword"},
                    "analysis_type": {"type": "keyword"},
                    "result": {"type": "nested"},
                    "created_at": {"type": "date"}
                }
            }
        }
        es.options(ignore_status=400).indices.create(index="analysis_results", body=analysis_results_index)

        print("[Elasticsearch] Indices created.")

    except Exception as e:
        print(f"[Elasticsearch] Error setting up Elasticsearch: {e}")

if __name__ == "__main__":
    print("Starting pipeline setup...")
    setup_postgres()
    setup_redis()
    setup_kafka()
    setup_elasticsearch()
    print("Pipeline setup complete!")
    