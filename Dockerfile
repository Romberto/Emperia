FROM python:3.11-slim

WORKDIR /app

COPY ./fast_application /app/fast_application
COPY ./fast_application/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app_main", "--host", "0.0.0.0", "--port", "8000"]

