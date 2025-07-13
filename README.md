rag-lite/
├─ docker-compose.yml
├─ .env.example
├─ backend/
│    ├─ Dockerfile
│    ├─ requirements.txt
│    ├─ main.py
│    ├─ db.py
│    ├─ rag.py
│    └─ sql/
│         └─ init.sql
└─ frontend/
     ├─ Dockerfile
     ├─ package.json
     ├─ tsconfig.json
     ├─ vite.config.ts
     ├─ tailwind.config.js
     ├─ postcss.config.js
     ├─ index.html
     ├─ index.css          ← all Tailwind directives
     └─ src/
          ├─ main.tsx
          ├─ App.tsx
          └─ api.ts




# as 'ubuntu' in your home directory
npm create vite@latest rag-lite-frontend -- --template react-ts
cd rag-lite


# Run local
in root folder run

`docker compose up -d db ollama api   # builds/starts only these three`

In frontend folder run
`npm run dev`


# Ollama embeddings endpoint requires a single-string "prompt".
see rag.py,  def embed_texts


# Test Query / ask
while UI  running
`curl -X POST http://localhost:8000/ask -d "question=ping?"`

# Probe each API hop manually
# A. Is /upload working?
curl -F "file=@sample.pdf" http://localhost:8000/upload

# B. Does embedding return quickly?
curl -X POST http://localhost:11434/api/embeddings \
     -H "Content-Type: application/json" \
     -d '{"model":"nomic-embed-text","prompt":["hello"]}'

# C. Does chat return?
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{"model":"tinyllama:1.1b-chat-v1-q4_0", "messages":[{"role":"user","content":"ping"}]}'

All three should answer in < 2 s.

If B and C are fast but A hangs, the slowdown is inside rag.py
(chunking, embedding loop, or DB insert).

# Check that the vector table isn’t exploding
A huge PDF with 512-token chunks can generate thousands of rows and dozens of MB of embeddings:


`docker compose exec db psql -U rag -d rag -c "SELECT COUNT(*) FROM documents;"`

# Watch live CPU / RAM usage

`docker stats`
ollama should hover ~250 % CPU for a second, then idle.

RSS for ollama ~3 GB, api <200 MB, db ~200 MB.

If api grows to >1 GB it may be buffering the entire PDF in memory—slice the file or process page-by-page.



# Common one-line fixes


| Symptom                               | Quick patch                                                                                                    |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Ollama chat takes >40 s               | Add `Environment="OLLAMA_NUM_THREAD=6"` in `ollama.service` or as an env-var in Compose to use all 3 CPU cores |
| `api` hangs right after `embed_texts` | Split the  list: call `/api/embeddings` every 100 chunks instead of one huge payload                           |
| DB insert crawls                      | Use `session.bulk_save_objects()` or `COPY` for very large PDFs                                                |
| Front-end shows spinner forever       | Add a 60 s timeout in `axios.post('/ask', …, {timeout: 60000})` and show a retry button                        |

### Test Ollama embeddings
docker run --rm --network rag-lite_default curlimages/curl:8.8.0 \
  -s http://ollama:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic-embed-text","prompt":"test"}'


# Quick verification of the Ollama endpoint

Make sure /api/generate really succeeds from inside the Compose network and
that TinyLlama is loaded:
# pull the model once if you haven't yet (≈ 1.2 GB, one-time)
`docker compose exec ollama ollama pull tinyllama:1.1b-chat-v1-q4_0`

# test generate directly
```
docker run --rm --network rag-lite_default curlimages/curl:8.8.0 \
  -s http://ollama:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"tinyllama:1.1b-chat-v1-q4_0","prompt":"ping?","stream":false}'
```
```
docker compose build --no-cache api
docker compose up -d --force-recreate api

```

# Inspect Container with Python Code

```docker compose exec -T api python - <<'PY'
import inspect, rag, textwrap, sys
print(textwrap.dedent(inspect.getsource(rag.answer_with_rag)))
PY

```


# Minimal rebuild sequence (after fixing the file location)

# 1. Stop and remove the old API container
docker compose rm -sf api      

# 2. Rebuild *without cache*
DOCKER_BUILDKIT=1 docker compose build --no-cache api

# 3. Start it fresh
docker compose up -d api

# 4. Sanity-check the code now inside
docker compose exec -T api python - <<'PY'
import inspect, rag, textwrap
print(textwrap.dedent(inspect.getsource(rag.answer_with_rag)))
PY



-------------
### Check Ollama response on terminal during processing
docker compose logs -f api ollama

### Models Ollama available
curl http://localhost:11434/api/tags   


### Checks
# 1. Is Ollama alive?
curl http://localhost:11434/api/tags            # should list tinyllama & nomic

# 2. Is the API container healthy?
curl http://localhost:8000/docs                 # FastAPI Swagger UI

# 3. Quickly embed text through the API
curl -X POST http://localhost:8000/ask -d "question=ping?"


#### Docker Container - Commands
docker compose exec db psql -U rag -d rag -c "\dt"      # list tables
# if none, then:
docker compose exec db psql -U rag -d rag -f /docker-entrypoint-initdb.d/00-init.sql

# verify the extension
docker compose exec db psql -U rag -d rag -c "\dx vector"
                          List of installed extensions
 Name   | Version |   Schema   |                     Description
--------+---------+------------+---------------------------------------------------
 vector | 0.5.0   | public     | vector data type and vector similarity search
(1 row)





Because TinyLlama is small, a single forward pass with a ~2 k-token context averages 250–350 ms on a 3-vCPU Contabo VPS, so end-to-end latency (including DB hit) usually stays < 900 ms.

------------

Front-end (React + Vite)

The UI is intentionally minimal; Vite’s dev server proxies API calls to localhost:8000 during development, while the production build is served by a micro-nginx inside the web container.
------------