from fastapi import FastAPI, UploadFile, File, Form, Depends
import io
from sqlalchemy.orm import Session
from db import get_session, Document
from rag import pdf_to_chunks, embed_texts, query_pgvector, answer_with_rag

app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_session)):
    chunks = pdf_to_chunks(io.BytesIO(await file.read()))
    vectors = embed_texts(chunks)
    for txt, vec in zip(chunks, vectors):
        db.add(Document(file_name=file.filename, chunk_text=txt, embedding=vec))
    db.commit()
    return {"status": "indexed", "chunks": len(chunks)}

@app.post("/ask")
async def ask(question: str = Form(...), db: Session = Depends(get_session)):
    return answer_with_rag(question, db)
