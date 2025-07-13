CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS documents (
  id          BIGSERIAL PRIMARY KEY,
  file_name   TEXT,
  chunk_text  TEXT,
  embedding   VECTOR(768)
);

CREATE INDEX IF NOT EXISTS ON documents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
