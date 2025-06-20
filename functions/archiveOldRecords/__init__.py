import datetime
import gzip
import json
import logging
import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, PartitionKey

COSMOS_DB_URL = os.environ["COSMOS_DB_URL"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]

BLOB_CONNECTION_STRING = "the blob connection string"
BLOB_CONTAINER = "billing-archive"

def main(mytimer: func.TimerRequest) -> None:
    logging.info("Starting archival job...")

    cutoff_date = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()
    
    cosmos_client = CosmosClient(COSMOS_DB_URL, credential=COSMOS_KEY)
    container = cosmos_client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)

    blob_service = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_container = blob_service.get_container_client(BLOB_CONTAINER)

    query = f"SELECT * FROM c WHERE c.date < '{cutoff_date}'"
    old_records = list(container.query_items(query, enable_cross_partition_query=True))

    for record in old_records:
        record_id = record["id"]
        json_data = json.dumps(record).encode("utf-8")
        compressed = gzip.compress(json_data)

        blob_name = f"{record_id}.json.gz"
        blob_container.upload_blob(name=blob_name, data=compressed, overwrite=True)
        container.delete_item(item=record_id, partition_key=record["partitionKey"])

    logging.info(f"Archived {len(old_records)} old billing records.")

