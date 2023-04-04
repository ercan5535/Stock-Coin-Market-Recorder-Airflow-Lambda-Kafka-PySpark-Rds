#!/bin/bash

# Copy app files to docker container
sudo docker cp ./app.py spark-worker:/opt/spark
sudo docker cp ./postgresql-42.5.1.jar spark-worker:/opt/spark

# Run spark app
sudo docker exec -d spark-worker \
        /opt/spark/bin/spark-submit \
        --master spark://{SPARK_MASTER_IP}:7077 \
        --jars /opt/spark/postgresql-42.5.1.jar \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.3 \
        /opt/spark/app.py {KAFKA_SERVER} {COIN_TOPIC} {STOCK_TOPIC} \
          {RDS_URL} {RDS_USER} {RDS_PW} {RDS_TABLE_COIN} {RDS_TABLE_STOCK}