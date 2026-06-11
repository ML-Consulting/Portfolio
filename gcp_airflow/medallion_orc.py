from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import pendulum
from bronze import bronze_main
from silver import silver_main
from gold import gold_main

from config import config

default_args = {
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag_bronze = DAG(
    dag_id="medallion_orc_dag",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="@daily",          # schedule replaces schedule_interval in Airflow 2.4+
    default_args=default_args,
)


with dag_bronze:
    task_bronze = PythonOperator(
        task_id="bronze_task",
        email_on_failure=True,
        email=["arrington.micah@gmail.com"],
        python_callable=bronze_main,
        op_kwargs={
            "project_id": config.project_id,
            "bucket_name": config.bucket_name
        }
    )

    task_silver = PythonOperator(
        task_id="silver_task",
        email_on_failure=True,
        email=["arrington.micah@gmail.com"],
        python_callable=silver_main,
        op_kwargs={
            "bucket_name": config.bucket_name,
            "raw_json_path": config.raw_json_path,
            "output_path": config.output_path
        }
    )

    task_gold = PythonOperator(
        task_id="gold_task",
        email_on_failure=True,
        email=["arrington.micah@gmail.com"],
        python_callable=gold_main,
        op_kwargs={
            "project_id": config.project_id,
            "dataset_id": config.dataset_id,
            "bucket_name": config.bucket_name
        }
    )

    task_dbt = BashOperator(
        task_id="dbt_task",
        email_on_failure=True,
        email=["arrington.micah@gmail.com"],
        bash_command=(
            f"cd {config.dbt_project_dir} && "
            "dbt run --profiles-dir . && "
            "dbt test --profiles-dir ."
        ),
        env={
            "DBT_PROJECT_ID": config.project_id,
            "DBT_DATASET": config.dataset_id,
            "DBT_BQ_LOCATION": "US",
        },
    )

    task_bronze >> task_silver >> task_gold >> task_dbt