FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system app && useradd --system --gid app --create-home app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

