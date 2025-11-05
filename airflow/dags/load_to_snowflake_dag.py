from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import sys

# Add scripts folder to PYTHONPATH
sys.path.append("/opt/airflow/scripts")
from minio_snowflake_loader import load_json_from_minio, load_dataframe_to_snowflake

# --- Airflow DAG Definition ---
default_args = {
    "owner": "marwen",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

with DAG(
    dag_id="load_minio_to_snowflake_dag",
    default_args=default_args,
    description="Load JSON data from MinIO to Snowflake staging (RAW schema)",
    schedule_interval=None,  # run manually for now
    start_date=datetime(2025, 11, 3),
    catchup=False,
    tags=["minio", "snowflake", "ingestion"],
) as dag:

    def load_minio_to_snowflake(**kwargs):
        """Extract JSON from MinIO and load into Snowflake."""
        bucket_name = kwargs.get("bucket_name", "raw-data")
        object_name = kwargs.get("object_name", "products_20251103_150306.json")
        table_name = kwargs.get("table_name", "PRODUCTS_RAW")

        df = load_json_from_minio(bucket_name, object_name)
        load_dataframe_to_snowflake(df, table_name)

    load_task = PythonOperator(
        task_id="load_minio_to_snowflake",
        python_callable=load_minio_to_snowflake,
        op_kwargs={
            "bucket_name": "raw-data",
            "object_name": "products_20251103_150306.json",
            "table_name": "PRODUCTS_RAW",
        },
    )

    load_task
