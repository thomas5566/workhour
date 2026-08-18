FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN python -m pip install -r requirements.txt

# Alembic files are included so Compose can run migrations as a separate,
# one-shot service before the API starts.
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations
COPY app ./app

# The API does not need root privileges at runtime. Files remain readable while
# a dedicated system user limits the impact of a compromised process.
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /usr/src/app
USER appuser

EXPOSE 5566

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5566/ready', timeout=2)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5566"]
