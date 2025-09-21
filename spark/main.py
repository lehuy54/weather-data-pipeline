from pyspark.sql.functions import *
from spark_utils import create_spark_session
from transform import get_weather_schema, transform_weather_df
import json
import os
from datetime import datetime, timezone

# Cấu hình
OFFSET_FILE = "/opt/spark/checkpoint/last_offsets.json"
TOPIC = "weather-data"
BOOTSTRAP_SERVERS = "kafka:9092"
DB_URL = "jdbc:postgresql://postgres:5432/weatherdb"
DB_TABLE = "weather_processed"
DB_USER = "postgres"
DB_PASS = "postgres"

def load_last_offset():
    """Đọc offset từ file checkpoint (nếu có)"""
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    print("⚠️ Offset file is empty. Starting from earliest.")
                    return None
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON in offset file: {e}. Starting from earliest.")
            return None
    return None

def save_last_offset(offsets):
    """Lưu offset vào file checkpoint"""
    with open(OFFSET_FILE, "w") as f:
        json.dump(offsets, f)

def process_weather_batch():
    spark = create_spark_session()
    schema = get_weather_schema()

    try:
        last_offset = load_last_offset()
        if last_offset:
            starting = json.dumps({TOPIC: {"0": last_offset + 1}})
        else:
            starting = "earliest"

        print(f"▶ Starting from offset: {starting}")

        df = spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS) \
            .option("subscribe", TOPIC) \
            .option("startingOffsets", starting) \
            .option("endingOffsets", "latest") \
            .load()
        
        # 2. Parse JSON data
        parsed_df = df.select(
            col("timestamp").alias("kafka_timestamp"),
            col("offset").alias("kafka_offset"),
            from_json(col("value").cast("string"), schema).alias("weather")
        ).select(
            "kafka_timestamp",
            "kafka_offset",
            "weather.*"
        )

        processed_df = transform_weather_df(parsed_df)

        if processed_df.count() > 0:
            # 4. Ghi vào PostgreSQL
            processed_df.write \
                .format("jdbc") \
                .option("url", DB_URL) \
                .option("dbtable", DB_TABLE) \
                .option("user", DB_USER) \
                .option("password", DB_PASS) \
                .option("driver", "org.postgresql.Driver") \
                .option("batchsize", 1000) \
                .option("isolationLevel", "NONE") \
                .mode("append") \
                .save()

            # 5. Lưu offset lớn nhất đã xử lý
            max_offset = processed_df.agg({"kafka_offset": "max"}).collect()[0][0]
            save_last_offset(max_offset)

            print(f"✅ Wrote records up to offset {max_offset} into DB.")
        else:
            print("ℹ️ No new records to process.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        spark.stop()
        print("🛑 Spark session stopped.")

if __name__ == "__main__":
    process_weather_batch()
