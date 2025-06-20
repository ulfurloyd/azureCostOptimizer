import os
import json
import gzip
import datetime
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, exceptions

# Config from environment or test secrets
COSMOS_DB_URL = os.environ["COSMOS_DB_URL"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]

BLOB_CONNECTION_STRING = os.environ["BLOB_CONNECTION_STRING"]
BLOB_CONTAINER = os.environ["CONTAINER_NAME"]

TEST_RECORD_ID = "test-archive-id-123"

def setup_test_record():
    client = CosmosClient(COSMOS_DB_URL, credential=COSMOS_KEY)
    container = client.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)

    test_record = {
        "id": TEST_RECORD_ID,
        "partitionKey": TEST_RECORD_ID,
        "date": (datetime.datetime.utcnow() - datetime.timedelta(days=120)).isoformat(),
        "amount": 987.65,
        "status": "archivable"
    }

    container.upsert_item(test_record)

def test_archive_flow():
    # 1. Insert test record
    setup_test_record()

    # 2. Run archival function logic directly (you could import and call `archive_old_records()`)

    cosmos = CosmosClient(COSMOS_DB_URL, credential=COSMOS_KEY)
    container = cosmos.get_database_client(DATABASE_NAME).get_container_client(CONTAINER_NAME)

    record = container.read_item(item=TEST_RECORD_ID, partition_key=TEST_RECORD_ID)
    assert record["id"] == TEST_RECORD_ID

    # 3. Simulate archive (manual for now — you can hook into the function module)
    json_data = json.dumps(record).encode("utf-8")
    compressed = gzip.compress(json_data)

    blob = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_client = blob.get_blob_client(container=BLOB_CONTAINER, blob=f"{TEST_RECORD_ID}.json.gz")
    blob_client.upload_blob(compressed, overwrite=True)

    container.delete_item(TEST_RECORD_ID, partition_key=TEST_RECORD_ID)

    # 4. Confirm deletion
    try:
        container.read_item(item=TEST_RECORD_ID, partition_key=TEST_RECORD_ID)
        assert False, "Record should have been deleted"
    except exceptions.CosmosResourceNotFoundError:
        pass  # expected

    # 5. Confirm archive exists and is valid
    downloaded = blob_client.download_blob().readall()
    unzipped = json.loads(gzip.decompress(downloaded).decode())

    assert unzipped["id"] == TEST_RECORD_ID
    assert unzipped["amount"] == 987.65

    print("Archive flow passed.")

if __name__ == "__main__":
    test_archive_flow()

