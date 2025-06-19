FROM python:3.11-slim

WORKDIR /app

COPY ./fast_application /app/fast_application
COPY ./fast_application/requarement.txt /app/requarement.txt

RUN pip install --no-cache-dir -r requarement.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "fast_application.main:app_main", "--host", "0.0.0.0", "--port", "8000"]
