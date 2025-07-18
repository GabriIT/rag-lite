# db.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy import Column, BigInteger, Text


from pgvector.sqlalchemy import Vector                 # ✅ right type

DATABASE_URL = os.getenv("DATABASE_URL")

# ---- compatibility shim ----------------------------------------
if DATABASE_URL.startswith("postgres://"):
    # SQLAlchemy 2.x needs the full dialect name
    DATABASE_URL = DATABASE_URL.replace("postgres://",
                                        "postgresql+psycopg2://", 1)
# ----------------------------------------------------------------



engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
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
