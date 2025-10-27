# AI Search Indexing Build Package Overview
Azure AI Search serves as a critical infrastructure component that enables:

- Schema selection for NL2SQL through semantic
- matching of user queries to database schemas
- Query caching to improve performance and reduce costs
- Column value storage for entity recognition and disambiguation


# Azure AI Search powers several critical features in the NL2SQL system:

## Schema Selection
The Schema Selection Agent uses AI Search to find the most relevant database tables and views based on the user's natural language query. This process involves:

## Extracting query intent from natural language
Sending a semantic search request to the Schema Store Index
Retrieving relevant database objects with their schemas
Selecting the appropriate schema for SQL generation

## Column Value Lookups
The system uses Azure AI Search to discover column values and entities in the database that match user queries. This allows:

## Entity disambiguation
- Entity recognition
- Value validation
- These lookups are performed through the get_column_values method in the AISearchConnector class.

## Query Caching
The Query Cache uses AI Search to:

- Store previously generated SQL queries with their natural language questions
- Match new questions to similar previously asked questions
Retrieve and reuse SQL queries for similar questions
- This caching mechanism improves performance and reduces costs by avoiding redundant SQL generation.

# Azure AI Search Queries
The system uses several types of queries to Azure AI Search:

## Vector Search Queries
Vector search uses embeddings to find semantically similar content. This is implemented in the run_ai_search_query method of the AISearchConnector class:

## Generate embeddings for the user query
Create a VectorizableTextQuery with appropriate fields
Send the query to Azure AI Search
Process and return the results
Vector search is particularly effective for semantic matching of questions to schemas or documents.

## Keyword Search
The system also supports traditional keyword search for exact matching, especially useful for column value lookups where fuzzy matching is needed

# AI Search Indexing Setup Detail Descrition

The associated scripts in this portion of the repository contains pre-built scripts to deploy the skillsets needed for nl2sql.

The steps here are same with "GETTING_STARTED" document, but here's with have more detailed instructions for your reference. 

## Steps for NL2SQL Index Deployment 

### Schema Store Index

**Execute the following commands in the `deploy_ai_search_indexes` directory:**

1. Create your `.env` file based on the provided sample `deploy_ai_search_indexes/.env.example`. Place this file in the same place in `deploy_ai_search_indexes/.env`.
2. Run `uv sync` within the `deploy_ai_search_indexes` directory to install dependencies.
    - Install the optional dependencies if you need a database connector other than TSQL. `uv sync --extra <DATABASE ENGINE>` , e.g., for PostgreSQL, use `uv sync --extra postgres`
    - See the supported connectors in `nl2sql/src/nl2sql_core/connectors` 

**Execute the following commands in the `deploy_ai_search_indexes/src/deploy_ai_search_indexes` directory:**

3. Adjust `text_2_sql_schema_store.py` with any changes to the index / indexer. The `get_skills()` method implements the skills pipeline. Make any adjustments here in the skills needed to enrich the data source.
4. Run `uv run deploy.py` with the following args:

    - `index_type nl2sql_schema_store`. This selects the `Text2SQLSchemaStoreAISearch` sub class.
    - `rebuild`. Whether to delete and rebuild the index.
    - `suffix`. Optional parameter that will apply a suffix onto the deployed index and indexer. This is useful if you want deploy a test version, before overwriting the main version.
    - `single_data_dictionary_file`. Optional parameter that controls whether you will be uploading a single data dictionary, or a data dictionary file per entity. By default, this is set to False.

### Column Value Store Index

**Execute the following commands in the `deploy_ai_search_indexes` directory:**

1. Create your `.env` file based on the provided sample `deploy_ai_search_indexes/.env.example`. Place this file in the same place in `deploy_ai_search_indexes/.env`.
2. Run `uv sync` within the `deploy_ai_search_indexes` directory to install dependencies.
    - Install the optional dependencies if you need a database connector other than TSQL. `uv sync --extra <DATABASE ENGINE>`
    - See the supported connectors in `nl2sql_core/src/nl2sql_core/connectors`.

**Execute the following commands in the `deploy_ai_search_indexes/src/deploy_ai_search_indexes` directory:**

3. Adjust `text_2_sql_column_value_store.py` with any changes to the index / indexer.
    - Korean Language support is added for column value search index.
    - Because analyzers are used to tokenize terms, you should assign an analyzer when the field is created. In fact, assigning an analyzer or indexAnalyzer to a field that has already been physically created isn't allowed (although you can change the searchAnalyzer property at any time with no impact to the index).

4. Run `uv run deploy.py` with the following args:

    - `index_type nl2sql_column_value_store`. This selects the `Text2SQLColumnValueStoreAISearch` sub class.
    - `rebuild`. Whether to delete and rebuild the index.
    - `suffix`. Optional parameter that will apply a suffix onto the deployed index and indexer. This is useful if you want deploy a test version, before overwriting the main version.

### Query Cache Index

**Execute the following commands in the `deploy_ai_search_indexes` directory:**

1. Create your `.env` file based on the provided sample `deploy_ai_search_indexes/.env.example`. Place this file in the same place in `deploy_ai_search_indexes/.env`.
2. Run `uv sync` within the `deploy_ai_search_indexes` directory to install dependencies.
    - Install the optional dependencies if you need a database connector other than TSQL. `uv sync --extra <DATABASE ENGINE>`
    - See the supported connectors in `nl2sql/src/nl2sql_core/connectors`.

**Execute the following commands in the `deploy_ai_search_indexes/src/deploy_ai_search_indexes` directory:**

3. Adjust `text_2_sql_query_cache.py` with any changes to the index. **There is an optional provided indexer or skillset for this cache. You may instead want the application code will write directly to it. See the details in the Text2SQL README for different cache strategies.**
4. Run `uv run deploy.py` with the following args:

    - `index_type nl2sql_query_cache`. This selects the `Text2SQLQueryCacheAISearch` sub class.
    - `rebuild`. Whether to delete and rebuild the index.
    - `suffix`. Optional parameter that will apply a suffix onto the deployed index and indexer. This is useful if you want deploy a test version, before overwriting the main version.
    - `enable_cache_indexer`. Optional parameter that will enable the query cache indexer. Defaults to False.
    - `single_cache__file`. Optional parameter that controls whether you will be uploading a single data dictionary, or a data dictionary file per entity. By default, this is set to False.

## ai_search.py & environment.py

This includes a variety of helper files and scripts to deploy the index setup. This is useful for CI/CD to avoid having to write JSON files manually or use the UI to deploy the pipeline.
