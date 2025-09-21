from pyspark.sql import SparkSession

def create_spark_session():
    spark = SparkSession.builder \
        .appName("WeatherBatchProcessor") \
        .master("spark://spark-master:7077") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark