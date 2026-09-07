# DataOps AI Copilot

Small Python project that explores how to build an LLM-powered data assistant using **structured outputs, tool calling and RAG**.

The application answers questions about transport incidents using two different sources of information:

* **Structured data** stored in SQLite, queried through Python tools.
* **Internal documentation** retrieved using a small RAG pipeline.

The LLM is responsible for understanding the user's request and deciding which tool to use. Data retrieval and calculations are handled by deterministic Python/SQL code.

## Planned features

* LLM API integration
* Structured outputs with Pydantic
* Tool calling
* SQLite queries
* Incident statistics with Python / SQL
* RAG over Markdown documentation
* Embeddings and vector search
* Simple REST API with FastAPI
* Dockerized application

## Architecture

```text
User
 │
 ▼
LLM
 │
 ├── get_incidents ─────────► SQLite
 │
 ├── get_incident_statistics ► Python / SQL
 │
 └── search_procedures ─────► RAG
                                │
                                ├── chunking
                                ├── embeddings
                                └── vector store
 │
 ▼
Validated response
```

The LLM does not access the database directly. It selects a tool and generates its arguments; the Python application validates and executes the operation before returning the result to the model.

## Example questions

```text
"What critical incidents are currently open?"

"Which line had the most incidents during the last 7 days?"

"When should a high-severity incident be escalated according to the internal procedure?"
```

## Tech stack

* Python
* LLM API
* Pydantic
* SQLite
* pandas
* FastAPI
* Docker

## Project status

Work in progress.
