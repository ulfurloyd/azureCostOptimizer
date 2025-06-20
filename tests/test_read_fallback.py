import os
import gzip
import json
from azure.storage.blob import BlobServiceClient

BLOB_CONN = os.environ["BLOB_CONNECTION_STRING"]
CONTAINER = os.environ["CONTAINER_NAME"]

def test_retrieve_sample_record():
    blob_service = BlobServiceClient.from_connection_string(BLOB_CONN)
    blob_client = blob_service.get_blob_client(container=CONTAINER, blob="sample-id.json.gz")

    blob_data = blob_client.download_blob().readall()
    data = json.loads(gzip.decompress(blob_data).decode())

    assert "id" in data
    assert data["amount"] >= 0
    print("Passed blob retrieval test")
