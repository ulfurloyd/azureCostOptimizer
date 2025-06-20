* defined a scheduled job that:
    * selects data older than 90 days
    * compresses it to save on blob storage space
    * uploads each record as a blob
    * deletes the record from Cosmos DB (after successful upload)
