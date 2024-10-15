from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType, LongType
from snowflake.connector.pandas_tools import write_pandas

# Initialize Spark Session
spark = SparkSession \
    .builder \
    .appName("EcommerceCustomerBehaviorAnalytics") \
    .getOrCreate()

# Define Kafka Source
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "customer_activity") \
    .load()

# Define schema for incoming data
schema = StructType() \
    .add("user_id", IntegerType()) \
    .add("event_type", StringType()) \
    .add("product_id", IntegerType()) \
    .add("timestamp", LongType())

# Parse Kafka data (Assume data is JSON encoded)
parsed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Perform transformations (e.g., aggregating user behavior)
aggregated_df = parsed_df.groupBy("event_type").count()

# Define the function to write the dataframe to Snowflake
def write_to_snowflake(df, epoch_id):
    snowflake_options = {
        "sfURL": "your_snowflake_account.snowflakecomputing.com",
        "sfUser": "your_username",
        "sfPassword": "your_password",
        "sfDatabase": "your_database",
        "sfSchema": "your_schema",
        "sfWarehouse": "your_warehouse",
        "sfRole": "your_role"
    }

    df.write \
        .format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "customer_behavior") \
        .mode("append") \
        .save()

# Write the stream to Snowflake
query = aggregated_df \
    .writeStream \
    .foreachBatch(write_to_snowflake) \
    .outputMode("update") \
    .start()

query.awaitTermination()
