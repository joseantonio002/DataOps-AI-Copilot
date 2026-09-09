from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.main import SYSTEM_PROMPT, run_agent
from app.rag.index import ProcedureIndex
from app.tools.procedures import configure_procedure_index
from app.tools.utils import PROJECT_ROOT


app = FastAPI(title="DataOps AI Copilot API")

procedure_index = ProcedureIndex.from_markdown_dir(PROJECT_ROOT / "docs")
configure_procedure_index(procedure_index)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    chat_history = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": request.question,
        },
    ]

    try:
        answer = run_agent(chat_history)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Agent execution failed",
        ) from exc

    return AskResponse(answer=answer)
