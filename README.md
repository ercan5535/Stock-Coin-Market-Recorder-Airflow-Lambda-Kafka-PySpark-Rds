# Description

In this project I created a data pipeline usign AWS technologies Lambda, EC2, RDS with Kafka, Spark and Airflow. <br>
It was a good practice for working with cloud technologies. <br>

Pipeline:
- Web scraping with Lambda functions is data source for pipeline. 2 Lambda functions are invoked by Airflow every 5 minutes. Lambda functions get data from websites(coinmarketcap, yahoofinance) and send it to Kafka topics
- Spark streaming listens Kafka topic and writes into RDS database. I create Spark cluster to do this because I just want to experience cluster mode and its configurations.

<img src="https://user-images.githubusercontent.com/67562422/226958671-4435a99e-61b5-40a1-a18b-c41d7d324280.png" width="800" height="300">
<br>
