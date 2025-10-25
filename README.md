# Nature Language to SQL (NL2SQL)
This repo provides code of NL-to-SQL (or NL2SQL) solutions.

It is intended that with the AI Search plugins and skills provided in this repository, are adapted and added to RAG application to improve the response quality.

> [!IMPORTANT]
>
> - This repository uses `uv` to manage dependencies and common utilities. See [uv](https://docs.astral.sh/uv/) for more details on how to get started.

## Components

- `./nl2sql` contains an three Multi-Shot implementations for NL2SQL generation and querying which can be used to answer questions backed by a database as a knowledge base. A **prompt based** and **vector based** approach are shown, both of which exhibit great performance in answering sql queries. Additionally, the vector based approach is shown which uses a **query cache** to further speed up generation.  With these plugins, your RAG application can now access and pull data from most SQL table exposed to it to answer questions.
- `./deploy_ai_search_indexes` provides an easy Python based utility for deploying an index, indexer and corresponding skillset for AI Search and for NL2SQL.

The above components have been successfully used on production RAG projects to increase the quality of responses.

> [!WARNING]
>
> - The code provided in this repo is a accelerator of the implementation and should be review / adjusted before being used in production.

## Contributing

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
