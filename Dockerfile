FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-lang-spanish \
    poppler-utils \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Añadimos fastapi, uvicorn y pydantic
RUN pip install --no-cache-dir fastapi uvicorn pydantic python-multipart pandas jinja2 Pillow psycopg2-binary pytest

COPY . /app

# Heisenberg: Forzar permisos de ejecución al copiar
COPY --chmod=755 entrypoint.sh /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
