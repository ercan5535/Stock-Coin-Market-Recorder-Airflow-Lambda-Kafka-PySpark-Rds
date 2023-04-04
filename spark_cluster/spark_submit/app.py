import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StringType, StructField, DoubleType, ArrayType, FloatType, MapType

# Get credentials for Kafka and RDS
KAFKA_BROKER_URL = sys.argv[1]
KAFKA_TOPIC_COIN = sys.argv[2]
KAFKA_TOPIC_STOCK = sys.argv[3]

RDS_URL = sys.argv[4]
RDS_USER = sys.argv[5]
RDS_PW = sys.argv[6]
RDS_TABLE_COIN = sys.argv[7]
RDS_TABLE_STOCK = sys.argv[8]

# Define the schemas
coin_schema = StructType([
    StructField("coin_name", StringType(), True),
    StructField("current_price", FloatType(), True)
])

stock_schema = StructType([
    StructField("stock_name", StringType(), True),
    StructField("current_price", FloatType(), True),
    StructField("previous_close", FloatType(), True)
])

# Create Spark Session
spark = SparkSession.builder.appName("StructuredStreaming").getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

# Read data from Kafka topics
df_coin = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", KAFKA_BROKER_URL) \
  .option("subscribe", KAFKA_TOPIC_COIN) \
  .option("startingOffsets", "earliest") \
  .load()

df_stock = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", KAFKA_BROKER_URL) \
  .option("subscribe", KAFKA_TOPIC_STOCK) \
  .option("startingOffsets", "earliest") \
  .load()

df_coin.printSchema()
#root
# |-- key: binary (nullable = true)
# |-- value: binary (nullable = true)
# |-- topic: string (nullable = true)
# |-- partition: integer (nullable = true)
# |-- offset: long (nullable = true)
# |-- timestamp: timestamp (nullable = true)
# |-- timestampType: integer (nullable = true)

df_stock.printSchema()
#root
# |-- key: binary (nullable = true)
# |-- value: binary (nullable = true)
# |-- topic: string (nullable = true)
# |-- partition: integer (nullable = true)
# |-- offset: long (nullable = true)
# |-- timestamp: timestamp (nullable = true)
# |-- timestampType: integer (nullable = true)

# Convert Value byte format to string format
df_coin = df_coin.selectExpr("CAST(value AS STRING)", "timestamp")
# +--------------------+--------------------+
# |               value|           timestamp|
# +--------------------+--------------------+
# |[{"coin_name": "b...|2023-03-06 18:50:...|

df_stock = df_stock.selectExpr("CAST(value AS STRING)", "timestamp")
# +--------------------+--------------------+
# |               value|           timestamp|
# +--------------------+--------------------+
# |[{"stock_name": "...|2023-03-06 21:38:...|


# Convert string type to array type and explode array
array_schema=ArrayType(StringType())

df_coin = df_coin.withColumn("array_value",from_json(col("value"),array_schema)) \
        .select(explode("array_value").alias("value"), "timestamp")
# +--------------------+--------------------+
# |               value|           timestamp|
# +--------------------+--------------------+
# |{"coin_name":"bit...|2023-03-06 18:50:...|
# |{"coin_name":"eth...|2023-03-06 18:50:...|
# |{"coin_name":"bnb...|2023-03-06 18:50:...|
# |{"coin_name":"dog...|2023-03-06 18:50:...|
# |{"coin_name":"sol...|2023-03-06 18:50:...|
# |{"coin_name":"ava...|2023-03-06 18:50:...|

df_stock = df_stock.withColumn("array_value",from_json(col("value"),array_schema)) \
        .select(explode("array_value").alias("value"), "timestamp")
# +--------------------+--------------------+
# |               value|           timestamp|
# +--------------------+--------------------+
# |{"stock_name":"Ap...|2023-03-06 18:50:...|
# |{"stock_name":"Te...|2023-03-06 18:50:...|
# |{"stock_name":"Am...|2023-03-06 18:50:...|
# |{"stock_name":"Al...|2023-03-06 18:50:...|
# |{"stock_name":"Me...|2023-03-06 18:50:...|
# |{"stock_name":"Ne...|2023-03-06 18:50:...|

# Parse values
df_coin = df_coin.select(from_json(col("value").cast("string"), coin_schema).alias("parsed_value"), "timestamp")
df_coin = df_coin.select("parsed_value.*", "timestamp")
 
# Convert column names same with AWS RDS Table
df_coin = df_coin.withColumnRenamed("coin_name", "coin") \
        .withColumnRenamed("current_price", "price") \
        .withColumnRenamed("timestamp", "date")
# +---------+--------+--------------------+
# |     coin|   price|                date|
# +---------+--------+--------------------+
# |  bitcoin|22470.52|2023-03-06 18:50:...|
# | ethereum| 1572.01|2023-03-06 18:50:...|
# |      bnb|  286.41|2023-03-06 18:50:...|
# | dogecoin| 0.07441|2023-03-06 18:50:...|
# |   solana|   20.83|2023-03-06 18:50:...|
# |avalanche|   16.42|2023-03-06 18:50:...|
 
df_stock = df_stock.select(from_json(col("value").cast("string"), stock_schema).alias("parsed_value"), "timestamp")
df_stock = df_stock.select("parsed_value.*", "timestamp")

# Convert column names same with AWS RDS Table
df_stock = df_stock.withColumnRenamed("stock_name", "stock") \
            .withColumnRenamed("current_price", "price") \
            .withColumnRenamed("timestamp", "date")
# +--------------------+------+--------------+--------------------+
# |               stock| price|previous_close|                date|
# +--------------------+------+--------------+--------------------+
# |   Apple Inc. (AAPL)|154.82|        151.03|2023-03-06 18:50:...|
# |  Tesla, Inc. (TSLA)|193.75|        197.79|2023-03-06 18:50:...|
# |Amazon.com, Inc. ...|  94.8|          94.9|2023-03-06 18:50:...|
# |Alphabet Inc. (GOOG)| 95.81|         94.02|2023-03-06 18:50:...|
# |Meta Platforms, I...|186.07|        185.25|2023-03-06 18:50:...|
# |Netflix, Inc. (NFLX)|316.96|        315.18|2023-03-06 18:50:...|

# Write datas into RDS tables
# Define the function to write to RDS
def writeToRDS_coin(df, epochId):
  df.write \
    .format("jdbc") \
    .option("url", RDS_URL) \
    .option("dbtable", RDS_TABLE_COIN) \
    .option("user", RDS_USER) \
    .option("password", RDS_PW) \
    .option("driver", "org.postgresql.Driver") \
    .mode("append") \
    .save()

def writeToRDS_stock(df, epochId):
  df.write \
    .format("jdbc") \
    .option("url", RDS_URL) \
    .option("dbtable", RDS_TABLE_STOCK) \
    .option("user", RDS_USER) \
    .option("password", RDS_PW) \
    .option("driver", "org.postgresql.Driver") \
    .mode("append") \
    .save()

# Write to RDS using foreachBatch
query = df_coin \
    .writeStream \
    .foreachBatch(writeToRDS_coin) \
    .start()

query = df_stock \
    .writeStream \
    .foreachBatch(writeToRDS_stock) \
    .start()

query.awaitTermination()
