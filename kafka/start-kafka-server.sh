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
sudo docker-compose down

# Remove all images
sudo docker rmi -f $(sudo docker images -aq)

# Run docker-compose file
sudo EC2_IP_ADDRESS={EC2_IP_ADDRESS} \
    KAFKA_TOPIC_COIN={COIN_TOPIC} \
    KAFKA_TOPIC_STOCK={STOCK_TOPIC} \
    docker-compose up -d

