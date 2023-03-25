import airflow

from datetime import timedelta
from bash_scripts import start_kafka, start_spark_master, start_spark_worker, spark_submit

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.sftp.operators.sftp import SFTPOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import Variable

# Get credentials from airfow variables
kafka = Variable.get("kafka", deserialize_json=True)
spark = Variable.get("spark", deserialize_json=True)
rds = Variable.get("rds", deserialize_json=True)

# Define DAG objects
default_args = {
    'owner': 'ercan',
    'retries': 1,
    'retry_delay': timedelta(seconds=15)   
}

with DAG(
    dag_id='make_servers_ready',
    default_args=default_args,
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval='@daily'
) as dag:
    # Define start dummy DAG
    start_operator = DummyOperator(task_id='begin-execution')

    # Ensure RDS coin_records table is exists
    check_coin_table = PostgresOperator(
        task_id="check_coin_table_exists",
        postgres_conn_id="rds_postgres",
        sql="""
        CREATE TABLE IF NOT EXISTS coin_records
        (
            id           serial PRIMARY KEY,
            coin         text,
            price        decimal,
            date         timestamp NOT NULL
        );"""
    )

    # Ensure RDS stock_record table is exists
    check_stock_table = PostgresOperator(
        task_id="check_stock_table_exists",
        postgres_conn_id="rds_postgres",
        sql="""
        CREATE TABLE IF NOT EXISTS stock_records
        (
            id                 serial PRIMARY KEY,
            stock              text,
            price              decimal,
            previous_close     decimal,
            date               timestamp NOT NULL
        );"""
    )

    # Make kafka ready
    run_kafka_bash = SSHOperator(
        task_id='make_kafka_ready',
        ssh_conn_id='kafka_instance_ssh',
        cmd_timeout=100,
        command=start_kafka.format(
            EC2_IP_ADDRESS=kafka["IP_ADDRESS"],
            COIN_TOPIC=kafka["COIN_TOPIC"],
            STOCK_TOPIC=kafka["STOCK_TOPIC"]
        )
    )
#
    # Make Spark Master ready
    run_spark_master_bash = SSHOperator(
        task_id='make_spark_master_ready',
        ssh_conn_id='spark_master_instance_ssh',
        cmd_timeout=100,
        command=start_spark_master
    )

    # Make Worker 1 ready
    run_spark_worker1_bash = SSHOperator(
        task_id='make_worker1_ready',
        ssh_conn_id='spark_worker1_instance_ssh',
        cmd_timeout=100,
        command=start_spark_worker.format(
            SPARK_MASTER_IP=spark["MASTER_INTERNAL_DNS"]
        )
    )

    # Make Worker 2 ready
    run_spark_worker2_bash = SSHOperator(
        task_id='make_worker2_ready',
        ssh_conn_id='spark_worker2_instance_ssh',
        cmd_timeout=100,
        command=start_spark_worker.format(
            SPARK_MASTER_IP=spark["MASTER_INTERNAL_DNS"]
        )
    )

    # Make Worker 3 ready
    run_spark_worker3_bash = SSHOperator(
        task_id='make_worker3_ready',
        ssh_conn_id='spark_worker3_instance_ssh',
        cmd_timeout=100,
        command=start_spark_worker.format(
            SPARK_MASTER_IP=spark["MASTER_INTERNAL_DNS"]
        )
    )

    # Load app files
    load_spark_app = SFTPOperator(
        task_id="load_app_to_worker",
        ssh_conn_id="spark_worker1_instance_ssh",
        local_filepath="/opt/airflow/dags/spark_cluster/spark_submit/app.py",
        remote_filepath="/home/ec2-user/app.py",
        operation="put",
    )

    load_spark_app_jar = SFTPOperator(
        task_id="load_app_jar_to_worker",
        ssh_conn_id="spark_worker1_instance_ssh",
        local_filepath="/opt/airflow/dags/spark_cluster/spark_submit/postgresql-42.5.1.jar",
        remote_filepath="/home/ec2-user/postgresql-42.5.1.jar",
        operation="put",
    )
   # Execute spark submit
    run_spark_submit_bash = SSHOperator(
        task_id='spark_submit',
        ssh_conn_id='spark_worker1_instance_ssh',
        cmd_timeout=100,
        command=spark_submit.format(
            SPARK_MASTER_IP=spark["MASTER_INTERNAL_DNS"],
            KAFKA_SERVER=kafka["HOST"]+':'+kafka["PORT"],
            COIN_TOPIC=kafka["COIN_TOPIC"],
            STOCK_TOPIC=kafka["STOCK_TOPIC"],
            RDS_URL = rds["RDS_URL"],
            RDS_USER = rds["RDS_USER"],
            RDS_PW = rds["RDS_PW"],
            RDS_TABLE_COIN = rds["RDS_TABLE_COIN"],
            RDS_TABLE_STOCK = rds["RDS_TABLE_STOCK"]
        )
    )

    start_operator >> [check_coin_table, check_stock_table]
    check_coin_table >> run_kafka_bash
    check_stock_table >> run_kafka_bash
    run_kafka_bash >> run_spark_master_bash
    run_spark_master_bash >> [run_spark_worker1_bash, run_spark_worker2_bash, run_spark_worker3_bash]
    run_spark_worker1_bash >> load_spark_app
    run_spark_worker2_bash >> load_spark_app
    run_spark_worker3_bash >> load_spark_app
    load_spark_app >> load_spark_app_jar
    load_spark_app_jar >> run_spark_submit_bash
