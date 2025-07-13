# db.py
from sqlalchemy import Column, BigInteger, Text
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine
from pgvector.sqlalchemy import Vector                 # ✅ right type

import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    file_name  = Column(Text)
    chunk_text = Column(Text)
    embedding  = Column(Vector(768))                   # 768-dim pgvector

def get_session() -> Session:
    with Session(engine) as session:
        yield session

# Auto-create table at first run (simple for demo)
Base.metadata.create_all(engine)
