FROM python:3.12-slim

ENV PORT 5000
EXPOSE 5000              


WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 PIP_DEFAULT_TIMEOUT=60

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install -r requirements.txt        # no apt involved

COPY . .


# use a shell CMD so $PORT expands at run‑time
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-5000}"]





# No EXPOSE needed – both sides now agree on whatever Dokku sets- > Port 5000
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
