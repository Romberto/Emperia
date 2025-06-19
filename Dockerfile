FROM python:3.11-slim

WORKDIR /app

COPY ./fast_application /app/fast_application

# Копируем requirements, если он внутри fast_application
COPY ./fast_application/requarement.txt /app/requarement.txt

RUN pip install --no-cache-dir -r requarement.txt

CMD ["uvicorn", "fast_application.main:app", "--host", "0.0.0.0", "--port", "8000"]
