import json

from scraping import coin_scraper
from kafka import KafkaProducer

def lambda_handler(event, context):
    # Get arguments from invoker
    COIN_LIST = event.get("coin_list")
    BASE_URL = event.get("base_url")
    PRICE_HTML_CLASS = event.get("price_html_class")
    
    KAFKA_SERVER = event.get("kafka_server")
    KAFKA_TOPIC_NAME = event.get("kafka_topic")
    
    # Define Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda x: json.dumps(x).encode('ascii')
    )
    
    # Get Coin data
    coin_data = coin_scraper(
        COIN_LIST,
        BASE_URL,
        PRICE_HTML_CLASS
    )
        
    # Push to kafka producer
    producer.send(KAFKA_TOPIC_NAME, coin_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps(coin_data)
    }