from pyspark.sql.types import *
from pyspark.sql.functions import *

def get_weather_schema():
    return StructType([
        StructField("name", StringType(), True),
        StructField("coord", StructType([
            StructField("lat", DoubleType(), True),
            StructField("lon", DoubleType(), True)
        ]), True),
        StructField("weather", ArrayType(StructType([
            StructField("main", StringType(), True),
            StructField("description", StringType(), True)
        ])), True),
        StructField("main", StructType([
            StructField("temp", DoubleType(), True),
            StructField("feels_like", DoubleType(), True),
            StructField("humidity", IntegerType(), True),
            StructField("pressure", IntegerType(), True)
        ]), True),
        StructField("wind", StructType([
            StructField("speed", DoubleType(), True),
            StructField("deg", IntegerType(), True)
        ]), True),
        StructField("processed_at", StringType(), True)
    ])

def transform_weather_df(parsed_df):
    return parsed_df.select(
            col("kafka_timestamp"),
            col("kafka_offset"),
            col("name").alias("city"),
            col("coord.lat").alias("latitude"),
            col("coord.lon").alias("longitude"),
            col("weather")[0]["main"].alias("weather_main"),
            col("weather")[0]["description"].alias("weather_description"),
            col("main.temp").alias("temperature"),
            col("main.feels_like").alias("feels_like"),
            col("main.humidity").alias("humidity"),
            col("main.pressure").alias("pressure"),
            coalesce(col("wind.speed"), lit(0.0)).alias("wind_speed"),
            col("processed_at")
        ).withColumn(
            "temp_category",
            when(col("temperature") < 15, "Cold")
            .when(col("temperature") < 28, "Mild") 
            .otherwise("Hot")
        ).withColumn(
            "processing_time",
            current_timestamp()
        )
