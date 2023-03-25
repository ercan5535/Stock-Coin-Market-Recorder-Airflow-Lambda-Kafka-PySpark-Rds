#!/bin/bash

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
sudo docker build -t spark-worker .

# Run docker image
sudo docker run \
  -e 'SPARK_MASTER={SPARK_MASTER_IP}:7077' \
  -p 8081:8081 \
  --name spark-worker \
  spark-worker
