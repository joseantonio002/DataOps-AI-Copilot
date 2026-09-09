from pathlib import Path

from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class ProcedureIndexChunk:
    def __init__(
        self,
        content: str,
        source: str,
        section: str,
        embedding: list[float],
    ):
        self.content = content
        self.source = source
        self.section = section
        self.embedding = embedding


class ProcedureIndex:
    def __init__(
        self,
        chunks: list[ProcedureIndexChunk],
        model: SentenceTransformer,
    ):
        self.chunks = chunks
        self.model = model

    @classmethod
    def from_markdown_dir(cls, docs_dir: Path) -> "ProcedureIndex":
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        if not docs_dir.exists() or not docs_dir.is_dir():
            return cls(chunks=[], model=model)

        chunk_data: list[tuple[str, str, str]] = []

        for markdown_path in sorted(docs_dir.glob("*.md")):
            text = markdown_path.read_text(encoding="utf-8").strip()

            if not text:
                continue

            chunk_data.extend(_split_markdown_by_h2(text, markdown_path.name))

        if not chunk_data:
            return cls(chunks=[], model=model)

        embedding_texts = [item[0] for item in chunk_data]
        embeddings = model.encode(embedding_texts).tolist()

        chunks = [
            ProcedureIndexChunk(
                content=content,
                source=source,
                section=section,
                embedding=embedding,
            )
            for (content, source, section), embedding in zip(chunk_data, embeddings)
        ]

        return cls(chunks=chunks, model=model)

    def search(self, question: str, top_k: int = 3) -> list[tuple[ProcedureIndexChunk, float]]:
        if not self.chunks:
            return []

        query_embedding = self.model.encode(question).tolist()

        scored_chunks = [
            (chunk, _cosine_similarity(query_embedding, chunk.embedding))
            for chunk in self.chunks
        ]

        scored_chunks.sort(key=lambda item: item[1], reverse=True)

        return scored_chunks[:top_k]


def _split_markdown_by_h2(text: str, source: str) -> list[tuple[str, str, str]]:
    lines = text.splitlines()
    document_title = source
    chunks: list[tuple[str, str, str]] = []
    current_section = "Overview"
    current_lines: list[str] = []

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith("# "):
            document_title = stripped_line.removeprefix("# ").strip() or source
            continue

        if stripped_line.startswith("## "):
            _append_chunk(
                chunks=chunks,
                document_title=document_title,
                source=source,
                section=current_section,
                lines=current_lines,
            )
            current_section = stripped_line.removeprefix("## ").strip() or "Untitled"
            current_lines = []
            continue

        current_lines.append(line)

    _append_chunk(
        chunks=chunks,
        document_title=document_title,
        source=source,
        section=current_section,
        lines=current_lines,
    )

    return chunks


def _append_chunk(
    chunks: list[tuple[str, str, str]],
    document_title: str,
    source: str,
    section: str,
    lines: list[str],
) -> None:
    body = "\n".join(lines).strip()

    if not body:
        return

    content = f"# {document_title}\n\n## {section}\n\n{body}"
    chunks.append((content, source, section))


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot_product / (left_norm * right_norm)
