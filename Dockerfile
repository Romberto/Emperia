FROM python:3.11-slim

WORKDIR /app

COPY ./fast_application /app

RUN pip install --no-cache-dir -r requarement.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
