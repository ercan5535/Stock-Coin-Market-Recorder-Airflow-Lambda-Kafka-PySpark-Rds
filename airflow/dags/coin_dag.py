import airflow
import json

from datetime import timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.lambda_function import AwsLambdaInvokeFunctionOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import Variable

# Get Kafka credentials from Airflow variables
kafka = Variable.get("kafka", deserialize_json=True)

# Define Lambda function input parameters
lambda_params={
    "coin_list":["bitcoin", "ethereum", "bnb", "dogecoin", "solana", "avalanche"],
    "base_url": "https://coinmarketcap.com/currencies/",
    "price_html_class": "priceValue",
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
    dag_id='coin_market_record',
    default_args=default_args,
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval='*/5 * * * *',
    catchup=False
) as dag:
    # Define start dummy DAG
    start_operator = DummyOperator(task_id='begin-execution')
 
    # Define DAGs to invoke lambda function
    invoke_coin_lambda = AwsLambdaInvokeFunctionOperator(
        task_id='invoke_coin_lambda',
        aws_conn_id='AWS_IAM',
        function_name='coin_record',
        invocation_type='RequestResponse',
        payload=json.dumps(lambda_params).encode('ascii')
    )

    start_operator >> invoke_coin_lambda