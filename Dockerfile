FROM python:3.11-slim

WORKDIR /app

# Скопировать всю папку fast_application внутрь контейнера
COPY ./fast_application /app/fast_application

# requirements.txt находится внутри fast_application, скопируем отдельно
COPY ./fast_application/requarement.txt /app/requarement.txt

# Установим зависимости
RUN pip install --no-cache-dir -r requarement.txt

# Добавим PYTHONPATH, чтобы Python находил fast_application
ENV PYTHONPATH=/app

# Запуск
CMD ["uvicorn", "fast_application.main:app_main", "--host", "0.0.0.0", "--port", "8000"]
