# The Problem
* billing records (~300kb each, over 2 million records) stored in Azure Cosmos DB
* old records (3+ months) rarely accessed but still incurring costs
* requirements:
    1. simple, easy to implement
    2. zero data loss or downtime
    3. no changes to existing r/w APIs
* bonus asks
    * architecture diagram
    * sample code/scripts for archival/retrieval

# The Solution (an idea)
a tiered storage system using:
* Cosmos DB (hot storage) for recent data (less than 3 months old)
* Azure Blob Storage (cold archive) for data older than 3 months

## core idea
* periodically move old billing records from Cosmos to blob storage in compressed JSON format
* set up a middleware function to fetch archived data when needed (transparent to the client)
* keep API interfaces unchanged by abstracting archival logic behind existing functions

# Architecture Diagram

# Workflow Logic

1. Archival Process (Azure Function / Timer Trigger)

2. Read API Logic (no changes to client)

3. Write API (no change) - continues writing to Cosmos

# Testing and Validation
* before deletion, test retrieval from blob for a sample set
* ensure compression doesn't lose fidelity
* benchmark cold read latency and verify that the fallback works

# Cost Benefit
* Cosmos costs scale with storage. archiving 90%+ of the two million records will reduce costs drastically
* Azure Blob Hot/Cool/Archive tiers allow fine grained pricing control
