import boto3
import json
from datetime import datetime

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "raw-data"

def upload_json_to_minio():
    """Uploads a sample JSON file to MinIO (simulating scraped data)."""
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )

    # Create bucket if it doesn’t exist
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' already exists.")
    except Exception:
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"✅ Bucket '{BUCKET_NAME}' created.")

    # Example product data (template)
    data = [
        {"id": "P001", "name": "Wireless Mouse", "price": 25.99, "brand": "Logitech"},
        {"id": "P002", "name": "Bluetooth Keyboard", "price": 45.5, "brand": "Microsoft"},
        {"id": "P003", "name": "USB-C Hub", "price": 29.9, "brand": "Anker"}
    ]

    file_name = f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=json.dumps(data),
        ContentType="application/json"
    )

    print(f"✅ Uploaded {file_name} to bucket '{BUCKET_NAME}'")
