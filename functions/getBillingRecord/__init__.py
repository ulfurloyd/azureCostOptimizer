import json
import gzip
import logging
import azure.functions as func
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient

COSMOS_DB_URL = os.environ["COSMOS_DB_URL"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]

BLOB_CONNECTION_STRING = "the blob connection string"
BLOB_CONTAINER = "billing-archive"

def main(req: func.HttpRequest) -> func.HttpResponse:
    record_id = req.route_params.get("record_id")
    if not record_id:
        return func.HttpResponse("Missing record_id", status+code=400)

    try:
        # Try Cosmos DB first
        cosmos_client = CosmosClient(COSMOS_DB_URL, credential=COSMOS_KEY)
        container = cosmos_client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)
        item = container.read_item(item=record_id, partition_key=record_id)
        return func.HttpResponse(json.dumps(item), mimetype="application/json")
    except Exception as cosmos_error:
        logging.info(f"CosmosDB lookup failed: {cosmos_error}")

    try:
        # Fallback to Blob Storage
        blob_service = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        blob_client = blob_service.get_blob_client(container=BLOB_CONTAINER, blob=f"{record_id}.json.gz")
        blob_data = blob_client.download_blob().readall()
        decompressed = gzip.decompress(blob_data).decode("utf-8")
        return func.HttpResponse(decompressed, mimetype="application/json")
    except Exception as blob_error:
        logging.error(f"Blob fallback also failed: {blob_error}")
        return func.HttpResponse("Record not found in either source.", status_code=404)
