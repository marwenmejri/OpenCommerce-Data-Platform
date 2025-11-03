# Use your stable Airflow base image
FROM apache/airflow:2.9.3-python3.11

# Switch to root to install dependencies
USER root

# Install required packages for MinIO and general data handling
RUN pip install --no-cache-dir \
    boto3 \
    pandas \
    requests

# Switch back to airflow user
USER airflow
