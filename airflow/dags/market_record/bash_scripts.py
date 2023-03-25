start_kafka = """
# Update system
sudo yum -y update

# Install & Start docker
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
sudo service docker start

# Install docker compose
sudo curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` | sudo tee /usr/local/bin/docker-compose > /dev/null
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Stop all existing containers
sudo docker-compose down

# Remove all images
sudo docker rmi -f $(sudo docker images -aq)

# Get docker compose file from s3
wget -O docker-compose.yaml https://ercan-bucket.s3.amazonaws.com/docker-compose.yaml

# Run docker-compose file
sudo EC2_IP_ADDRESS={EC2_IP_ADDRESS} \
    KAFKA_TOPIC_COIN={COIN_TOPIC} \
    KAFKA_TOPIC_STOCK={STOCK_TOPIC} \
    docker-compose up -d
"""

start_spark_master = """
# Update system
sudo yum -y update

# Install & Start docker
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
sudo service docker start

# Install docker compose
sudo curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` | sudo tee /usr/local/bin/docker-compose > /dev/null
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Stop all existing containers
sudo docker stop $(sudo docker ps -aq)

# Remove all containers
sudo docker rm $(sudo docker ps -aq)

# Remove all images
sudo docker rmi -f $(sudo docker images -aq)

# Build docker image
sudo docker pull ercan5535/spark-master:1.0

# Run docker image
sudo docker run -d \
  -p 8080:8080 \
  -p 7077:7077 \
  --name spark-master \
  ercan5535/spark-master:1.0
"""

start_spark_worker = """
# Update system
sudo yum -y update

# Install & Start docker
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
sudo service docker start

# Install docker compose
sudo curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` | sudo tee /usr/local/bin/docker-compose > /dev/null
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Stop all existing containers
sudo docker stop $(sudo docker ps -aq)

# Remove all containers
sudo docker rm $(sudo docker ps -aq)

# Remove all images
sudo docker rmi -f $(sudo docker images -aq)

# Build docker image
sudo docker pull ercan5535/spark-worker:1.0

# Run docker image
sudo docker run -d \
  -e 'SPARK_MASTER={SPARK_MASTER_IP}:7077' \
  -p 8081:8081 \
  --name spark-worker \
  ercan5535/spark-worker:1.0
"""

spark_submit = """
# Copy app files to docker container
sudo docker cp ./app.py spark-worker:/opt/spark
sudo docker cp ./postgresql-42.5.1.jar spark-worker:/opt/spark

# Run spark app
sudo docker exec -d spark-worker \
        /opt/spark/bin/spark-submit \
        --jars /opt/spark/postgresql-42.5.1.jar \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.3 \
        /opt/spark/app.py {KAFKA_SERVER} {COIN_TOPIC} {STOCK_TOPIC} \
          {RDS_URL} {RDS_USER} {RDS_PW} {RDS_TABLE_COIN} {RDS_TABLE_STOCK}
"""