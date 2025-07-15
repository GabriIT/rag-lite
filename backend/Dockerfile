FROM python:3.12-slim
WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 PIP_DEFAULT_TIMEOUT=60

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install -r requirements.txt        # no apt involved

COPY . .

# No EXPOSE needed – both sides now agree on whatever Dokku sets- > Port 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
