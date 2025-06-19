FROM python:3.11-slim

# Установим рабочую директорию
WORKDIR /app

# Копируем весь код в контейнер в /app
COPY ./fast_application /app/fast_application
COPY ./fast_application/requarement.txt /app/requarement.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requarement.txt

# Устанавливаем PYTHONPATH, чтобы fast_application стал импортируемым модулем
ENV PYTHONPATH=/app

# Запускаем uvicorn
CMD ["uvicorn", "fast_application.main:app", "--host", "0.0.0.0", "--port", "8000"]
