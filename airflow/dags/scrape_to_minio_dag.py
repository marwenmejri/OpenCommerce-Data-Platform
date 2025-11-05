from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
import sys
import os

# Add scripts path to Python path
sys.path.append("/opt/airflow/scripts")

# Import the upload function from scripts
from upload_to_minio import upload_json_to_minio

# Default args for the DAG
default_args = {
    "owner": "marwen",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define DAG
with DAG(
    dag_id="upload_to_minio_dag",
    description="Upload sample JSON data to MinIO (Landing Zone)",
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval=None,  # Manual trigger for now
    catchup=False,
    tags=["minio", "ingestion", "stage1"],
) as dag:

    upload_to_minio_task = PythonOperator(
        task_id="upload_json_to_minio",
        python_callable=upload_json_to_minio,
    )

    upload_to_minio_task
