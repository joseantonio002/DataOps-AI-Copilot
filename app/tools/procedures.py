from pydantic import BaseModel

from app.rag.index import ProcedureIndex


class ProcedureChunk(BaseModel):
    content: str
    source: str
    section: str
    score: float


class SearchProceduresResult(BaseModel):
    results: list[ProcedureChunk]


_procedure_index: ProcedureIndex | None = None


def configure_procedure_index(procedure_index: ProcedureIndex) -> None:
    global _procedure_index
    _procedure_index = procedure_index


def search_procedures(question: str) -> SearchProceduresResult:
    if _procedure_index is None:
        raise RuntimeError("Procedure index has not been configured")

    matches = _procedure_index.search(question=question, top_k=3)

    return SearchProceduresResult(
        results=[
            ProcedureChunk(
                content=chunk.content,
                source=chunk.source,
                section=chunk.section,
                score=score,
            )
            for chunk, score in matches
        ]
    )
