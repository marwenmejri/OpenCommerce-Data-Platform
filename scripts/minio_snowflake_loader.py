import os
import json
import pandas as pd
from io import BytesIO
from minio import Minio
import snowflake.connector

def load_json_from_minio(bucket_name, object_name):
    client = Minio(
        os.getenv("MINIO_ENDPOINT", "minio:9000"),
        access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
        secure=False
    )

    data = client.get_object(bucket_name, object_name)
    json_data = json.loads(data.read().decode("utf-8"))
    return pd.DataFrame(json_data)

def load_dataframe_to_snowflake(df, table_name):
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )
    cs = conn.cursor()

    # Create the table dynamically if not exists
    cols = ", ".join([f"{c} STRING" for c in df.columns])
    cs.execute(f"CREATE OR REPLACE TABLE {table_name} ({cols})")

    # Write data into Snowflake
    for _, row in df.iterrows():
        values = ", ".join([f"'{str(v)}'" for v in row.values])
        cs.execute(f"INSERT INTO {table_name} VALUES ({values})")

    conn.commit()
    cs.close()
    conn.close()
    print(f"✅ Loaded {len(df)} records into {table_name}")

if __name__ == "__main__":
    df = load_json_from_minio("opencommerce", "products/sample.json")
    load_dataframe_to_snowflake(df, "PRODUCTS_RAW")
