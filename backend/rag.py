# rag.py  – end-to-end RAG helpers for FastAPI backend
import os, textwrap, httpx, json
from typing import List
from PyPDF2 import PdfReader
from sqlalchemy import text
from sqlalchemy.orm import Session

OLLAMA = os.environ["OLLAMA_URL"]           # e.g. http://ollama:11434

### Debugging
# import time, logging
# log = logging.getLogger(__name__)

# t0 = time.perf_counter()
# vectors = embed_texts(chunks)
# log.info("embeddings %.2fs", time.perf_counter() - t0)

# t1 = time.perf_counter()
# session.bulk_save_objects([...])
# session.commit()
# log.info("db insert %.2fs", time.perf_counter() - t1)



# ---------------------------------------------------------------------------
# 1.  PDF → text chunks
# ---------------------------------------------------------------------------
def pdf_to_chunks(fh, max_len: int = 512) -> List[str]:
    """Read a PDF file handle and return ~max_len-char sentence-wrapped chunks."""
    reader = PdfReader(fh)
    whole_text = " ".join(p.extract_text() or "" for p in reader.pages)
    return textwrap.wrap(whole_text, max_len, break_long_words=False)


# ---------------------------------------------------------------------------
# 2.  Text → 768-d embeddings  (nomic-embed-text via Ollama)
# ---------------------------------------------------------------------------
# def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return a 768-float embedding for each text string."""
    out: List[List[float]] = []
    for t in texts:                            # Ollama’s API wants ONE string
        r = httpx.post(
            f"{OLLAMA}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": t},
            timeout=60,
        )
        r.raise_for_status()
        j = r.json()

        if "data" in j:               # Ollama ≤ 0.1.x
            out.append(j["data"][0]["embedding"])
        elif "embeddings" in j:       # Ollama 0.2 – 0.8
            out.append(j["embeddings"][0])
        elif "embedding" in j:        # Ollama 0.9 (single result)
            out.append(j["embedding"])
        else:
            raise RuntimeError(f"Unexpected embeddings JSON: {json.dumps(j)[:200]}")
    return out




def embed_texts(texts):
    for attempt in range(2):
        r = httpx.post(f"{OLLAMA}/api/embeddings",
                       json={"model":"nomic-embed-text","prompt": texts[0]},
                       timeout=60)
        if r.status_code == 404 and attempt == 0:
            # try to pull the model once
            httpx.post(f"{OLLAMA}/api/pull",
                       json={"name":"nomic-embed-text"}, timeout=600).raise_for_status()
            continue
        r.raise_for_status()
        break
    data = r.json()
    return [data.get("embedding") or data["data"][0]["embedding"]]


# ---------------------------------------------------------------------------
# 3.  ANN search in pgvector
# ---------------------------------------------------------------------------
def query_pgvector(session: Session, q_vec: List[float], k: int = 4) -> List[str]:
    """Return the k nearest chunk_text rows by cosine/inner-product distance."""
    vec_lit = "[" + ",".join(f"{x:.6f}" for x in q_vec) + "]"

    sql = text(f"""
      SELECT chunk_text
      FROM documents
      ORDER BY embedding <-> '{vec_lit}'::vector
      LIMIT :k
    """)
    rows = session.execute(sql, {"k": k}).fetchall()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# 4.  TinyLlama answer generation
# ---------------------------------------------------------------------------
SYSTEM = "You answer strictly from the provided CONTEXT."
TEMPLATE = "CONTEXT:\n{ctx}\n\nQuestion: {q}\nAnswer:"


def answer_with_rag(question: str, db: Session) -> dict:
    # 4-step pipeline --------------------------------------------------------
    q_vec  = embed_texts([question])[0]            # (a) embed question
    ctx_ls = query_pgvector(db, q_vec)             # (b) retrieve top-k chunks
    ctx    = "\n---\n".join(ctx_ls)

    prompt = f"{SYSTEM}\n\n" + TEMPLATE.format(ctx=ctx, q=question)

    r = httpx.post(
        f"{OLLAMA}/api/generate",                  # Ollama ≥0.9 single-shot
        json={
            "model": "tinyllama:1.1b-chat-v1-q4_0",
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    r.raise_for_status()
    answer = r.json().get("response", "").strip()

    return {"response": answer, "context": ctx_ls}
