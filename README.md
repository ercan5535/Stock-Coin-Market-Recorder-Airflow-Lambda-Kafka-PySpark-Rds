# Description

In this project I created a data pipeline usign AWS technologies Lambda, EC2, RDS with Kafka, Spark and Airflow. <br>
It was a good practice for working with cloud technologies. Spark, Lambda and Kafka folders are just for representation for cloud parts. All necessary files are defined under Airflow folder. <br>

Pipeline:
- Web scraping with Lambda functions is data source for pipeline. 2 Lambda functions are invoked by Airflow every 5 minutes. Lambda functions get data from websites(coinmarketcap, yahoofinance) and send it to Kafka topics
- Spark streaming listens Kafka topic and writes into RDS database. I create Spark cluster to do this because I just want to experience cluster mode and its configurations.

<img src="https://user-images.githubusercontent.com/67562422/226958671-4435a99e-61b5-40a1-a18b-c41d7d324280.png" width="800" height="300">
<br>

# Airflow:
Air flow is only component works on local machine. We can invokes lambda function with schedule and start our cloud components. It can be run by docker-compose up command. The <b>airflow_variables.json</b> should be uploaded Airflow variables to necessary variables.
```bash
├── docker-compose.yaml
├── airflow_variables.json
├── dags
│   ├── coin_dag.py
│   ├── make_servers_ready.py
│   └── stock_dag.py
├── instance_pem_files
│   ├── kafka-key.pem
│   ├── spark-master-key.pem
│   ├── spark-slave-1.pem
│   ├── spark-slave-2.pem
│   └── spark-slave-3.pem
└── market_record
    ├── bash_scripts.py
    └── spark_submit
        ├── app.py
        └── postgresql-42.5.1.jar
```

There 3 dags in airflow:
1) coin_market_record: <br>
 This dags runs every 5 minutes and invoke Lambda function to scrape coin market website for given coin list and push data to Kafka
2) stock_market_record: <br>
 This dags runs every 5 minutes between 2pm and 9pm Monday through Friday(NASDAQ work time for utc) and invoke Lambda function to scrape stock market website for given stock list and push datas to Kafka
3) make_servers_ready: <br>
 It basically runs sql command or bash scripts(market_record/bash_scripts.py) with ssh/postgres connection and make sure every component (RDS db, Kafka server and Spark cluster) ready before starting pipeline. For the ssh connection, pem files located under the instance_pem_files folder are used.<br>
 Makes servers ready steps:
    - <b>RDS</b>: Ensures coin market and stock market tables are exists on RDS db with CREATE TABLE IF NOT EXISTS sql command.
    - <b>Kafka</b>: Runs start_kafka bash script to make Kafka server is ready on ec2 instance. Bash scripts downloads docker-compose file from s3 and run it on ec2 inctance. Docker-compose file makes kafka server is working and 2 topics are created for coin and stock market data.
    - <b>Spark Master</b>: runs start_spark_master bash script to make Spark Master node ready on ec2 instance. Bash script pull docker image from dockerhub and run it on ec2 instance. Docker file starts Spark Master node. Now we can connect worker nodes to master node.
    - <b>Spark Workers</b>: runs start_spark_workers bash scripts to make Spark Worker nodes are ready on 3 ec2 instances. Bash script pull docker image from dockerhub and run it on ec2 instance. Docker file starts Spark Worker node and connects to Spark Master.
    - <b>Spark Submit</b>: first push spark app.py and postgres jdbc driver then run spark_submit bash command on worker node1. It starts spark app on all spark cluster.
<img src="https://user-images.githubusercontent.com/67562422/229861412-f4b4a483-4f6d-4bb4-b977-4725059ecb65.png" width="1000" height="300">
 
### Airflow connections
<img src="https://user-images.githubusercontent.com/67562422/229768996-c7b87996-c636-48a3-b25d-d54a66823955.png" width="800" height="300">

#### ssh connection example for ec2 instance
<img src="https://user-images.githubusercontent.com/67562422/229769201-aa899c42-dd62-4c18-b46d-95c485503cac.png" width="800" height="300">




### Spark Master Web UI: <br>
<img src="https://user-images.githubusercontent.com/67562422/229760928-50f24f36-e53a-4432-b1d4-bdedf522685d.png" width="800" height="300">
