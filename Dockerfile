FROM python:3.12-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --system --uid 10001 --create-home appuser
COPY app ./app
COPY assets ./assets
COPY scripts/generate_traffic.py ./scripts/generate_traffic.py
ARG RELEASE_VERSION=1.0.0
ARG INCIDENT_MODE=off
ENV APP_VERSION=${RELEASE_VERSION} INCIDENT_MODE=${INCIDENT_MODE}
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
