FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app \
    && mkdir -p /data /app/staticfiles \
    && chown -R app:app /app /data

COPY requirements.txt .
RUN pip install --requirement requirements.txt

COPY --chown=app:app . .

EXPOSE 8000
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]
