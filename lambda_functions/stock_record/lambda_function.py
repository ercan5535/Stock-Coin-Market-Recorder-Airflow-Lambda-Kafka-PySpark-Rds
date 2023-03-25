import json

from scraping import stock_scraper
from kafka import KafkaProducer


def lambda_handler(event, context):
    # Get arguments from invoker
    STOCK_LIST = event.get("stock_list")
    BASE_URL = event.get("base_url")

    STOCK_NAME_HTML_CLASS = event.get("stock_name_html_class")
    PREVIOUS_CLOSE_HTML_CLASS = event.get("previouse_close_html_class")
    PRICE_HTML_CLASS = event.get("price_html_class")

    KAFKA_SERVER = event.get("kafka_server")
    KAFKA_TOPIC_NAME = event.get("kafka_topic")
    
    # Define Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda x: json.dumps(x).encode('ascii')
    )
    
    # Get Stock data
    stock_data = stock_scraper(
        STOCK_LIST,
        BASE_URL,
        STOCK_NAME_HTML_CLASS,
        PREVIOUS_CLOSE_HTML_CLASS,
        PRICE_HTML_CLASS
    )

    # Push to Kafka topic
    producer.send(KAFKA_TOPIC_NAME, stock_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps(stock_data)
    }