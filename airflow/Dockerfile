# Start from the official Airflow image
FROM apache/airflow:2.9.3-python3.11

# Switch to root to install dependencies
USER root

# Install OS-level dependencies if needed (optional)
RUN apt-get update && apt-get install -y \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy your custom requirements
COPY ./requirements-airflow.txt /requirements-airflow.txt

# Revert to airflow user for security and for package installations
USER airflow

# Install additional Python packages for Airflow DAGs
RUN pip install --no-cache-dir -r /requirements-airflow.txt

