import airflow
import json

from datetime import timedelta, datetime
from airflow import DAG
from airflow.providers.amazon.aws.operators.lambda_function import AwsLambdaInvokeFunctionOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import Variable

# Get Kafka credentials from Airflow variables
kafka = Variable.get("kafka", deserialize_json=True)
scrape_params = Variable.get("stock_scraping", deserialize_json=True)

# Define Lambda function input parameters
lambda_params={
    "stock_list": scrape_params["stock_list"],
    "base_url": scrape_params["base_url"],
    "stock_name_html_class": scrape_params["stock_name_html_class"],
    "previouse_close_html_class": scrape_params["previouse_close_html_class"],
    "price_html_class": scrape_params["price_html_class"],
    "kafka_server": kafka["IP_ADDRESS"],
    "kafka_topic": kafka["COIN_TOPIC"]
}

# Define DAG objects
default_args = {
    'owner': 'ercan',
    'retries': 1,
    'retry_delay': timedelta(seconds=15)   
}

with DAG(
    dag_id='stock_market_record',
    default_args=default_args,
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval='*/5 14-21 * * 1-5',
    catchup=False
) as dag:
    # Define start dummy DAG
    start_operator = DummyOperator(task_id='begin-execution')
 
    # Define coin records DAG
    invoke_lambda = AwsLambdaInvokeFunctionOperator(
        task_id='invoke_stock_lambda',
        aws_conn_id='AWS_IAM',
        function_name='stock_record',
        invocation_type='RequestResponse',
        payload=json.dumps(lambda_params).encode('ascii')
    )

    start_operator >> invoke_lambda




