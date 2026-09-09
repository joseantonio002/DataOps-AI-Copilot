# DataOps AI Copilot

Small Python project for exploring how LLM applications work with **tool calling**, **structured outputs**, **SQLite data access**, **RAG over Markdown documentation**, and a minimal **FastAPI** interface.

The goal of the project is not to be a production platform. It is intentionally simple so each part can be tested and understood independently.

## What It Does

The assistant answers questions about transport operational incidents using three tools:

* `get_incidents`: retrieves individual incidents from SQLite.
* `get_incident_statistics`: calculates aggregate incident counts by line.
* `search_procedures`: retrieves relevant chunks from internal Markdown procedures using embeddings and cosine similarity.

The LLM decides which tool to call. Python validates the tool arguments with Pydantic, executes deterministic code, and sends the tool result back to the LLM so it can produce the final answer.

## Project Structure

```text
DataOps-AI-Copilot/
├── app/
│   ├── __main__.py          # python -m app entrypoint, starts the CLI
│   ├── main.py              # CLI, LLM call, tool definitions, tool registry, agent loop
│   ├── main_api.py          # FastAPI app
│   ├── config.yaml
│   ├── rag/
│   │   └── index.py         # simple in-memory Markdown RAG index
│   └── tools/
│       ├── incidents.py
│       ├── procedures.py
│       ├── statistics.py
│       └── utils.py
├── data/
│   ├── incidents.csv
│   └── incidents.db
├── docs/
│   ├── escalation_policy.md
│   ├── security_levels.md
│   └── sla.md
└── README.md
```

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv app/.venv
source app/.venv/bin/activate
pip install -r app/requirements.txt
```

Create the SQLite database from the sample CSV data:

```bash
python -m app.populate_db
```

Create a `.env` file in the repository root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

The project expects the SQLite database at:

```text
data/incidents.db
```

The `populate_db` command reads `data/incidents.csv` and creates or updates that database.

## Running The CLI

From the repository root:

```bash
python -m app
```

The package entrypoint `app/__main__.py` intentionally starts the CLI. This keeps the simplest workflow for experimenting from the terminal.

## Running The API

The API is a separate module in the same package:

```bash
uvicorn app.main_api:app --reload
```

If you are not using an activated virtual environment:

```bash
app/.venv/bin/uvicorn app.main_api:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What critical incidents are currently open?"}'
```

Response shape:

```json
{
  "answer": "..."
}
```

The API is stateless. Every `/ask` request creates a new conversation containing only the system prompt and the current user question.

## Example Prompts

Prompts that should use `get_incidents`:

```text
What critical incidents are currently open?
List open incidents on line L2.
Show me high severity incidents that are still unresolved.
```

Prompts that should use `get_incident_statistics`:

```text
Which line had the most incidents during the last 7 days?
How many incidents were opened in the last 30 days by line?
Compare incident volume between L1 and L3 over the last 14 days.
```

Prompts that should use `search_procedures`:

```text
When should a high severity incident be escalated?
What is the SLA target for critical incidents?
What is the difference between medium and high severity incidents?
```

Prompts that may combine database tools and procedures:

```text
Find open critical incidents and explain the escalation policy that applies to them.
Which line has the most recent incidents, and what SLA rules should operators consider?
```

## How It Works

```text
User question
    ↓
LLM
    ↓
Tool selection
    ↓
Pydantic argument validation
    ↓
Python tool execution
    ↓
Tool result returned to the LLM
    ↓
Final answer
```

For structured incident data, the tools query SQLite directly.

For internal documentation, the project builds a small in-memory RAG index from `docs/*.md` when the CLI or API starts. The documents are split by Markdown `##` headings, embedded with `sentence-transformers/all-MiniLM-L6-v2`, and searched with cosine similarity. No vector database or RAG framework is used.

## Why CLI And API Live Together

This repository is a learning project for experimenting with LLM calls, tools, structured outputs, and RAG. The CLI and API share the same package and reuse the same agent code to keep the project small.

`python -m app` starts the CLI because that is the default package entrypoint. To run the HTTP interface, start the FastAPI module explicitly with `uvicorn app.main_api:app --reload`.

## Tech Stack

* Python
* Groq Chat Completions API
* Pydantic
* SQLite
* sentence-transformers
* FastAPI
* Uvicorn

## Notes

* The LLM never queries the database directly.
* Tool arguments are validated before execution.
* The RAG tool retrieves documentation chunks only; it does not call another LLM.
* The API does not store chat history or sessions.
* Docker, authentication, streaming, and production deployment concerns are intentionally out of scope for now.
