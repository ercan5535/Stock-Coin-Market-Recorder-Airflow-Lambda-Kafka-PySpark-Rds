# Description

In this project I created a data pipeline usign AWS technologies Lambda, EC2, RDS with Kafka, Spark and Airflow. <br>
It was a good practice for working with cloud technologies. <br>

Pipeline:
- Web scraping with Lambda functions is data source for pipeline. 2 Lambda functions are invoked by Airflow every 5 minutes. Lambda functions get data from websites(coinmarketcap, yahoofinance) and send it to Kafka topics
- Spark streaming listens Kafka topic and writes into RDS database. I create Spark cluster to do this because I just want to experience cluster mode and its configurations.

<img src="https://user-images.githubusercontent.com/67562422/226958671-4435a99e-61b5-40a1-a18b-c41d7d324280.png" width="800" height="300">
<br>

# Airflow:

```bash
├── airflow
│   ├── docker-compose.yaml
│   ├── dags
│   │   ├── coin_dag.py
│   │   ├── make_servers_ready.py
│   │   └── stock_dag.py
│   ├── instance_pem_files
│   │   ├── kafka-key.pem
│   │   ├── spark-master-key.pem
│   │   ├── spark-slave-1.pem
│   │   ├── spark-slave-2.pem
│   │   └── spark-slave-3.pem
│   └── market_record
│       ├── bash_scripts.py
│       ├── make_servers_ready.py
│       └── stock_dag.py
```

### Airflow connections
<img src="https://user-images.githubusercontent.com/67562422/229768996-c7b87996-c636-48a3-b25d-d54a66823955.png" width="800" height="300">
ssh connection example for ec2 instance
<img src="https://user-images.githubusercontent.com/67562422/229769201-aa899c42-dd62-4c18-b46d-95c485503cac.png" width="800" height="300">




Spark Master Web UI: <br>
<img src="https://user-images.githubusercontent.com/67562422/229760928-50f24f36-e53a-4432-b1d4-bdedf522685d.png" width="800" height="300">
