* key notes
    * assumes `record_id` is both the document ID and partition key (can be adjusted if needed)
    * uses `.json.gz` files for archived data to save space
    * transparent to the client - works with the same `GET /billing/{id}` route regardless of storage layer
