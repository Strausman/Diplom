FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev

# Копируем файл requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем код приложения в контейнер
COPY . .

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочий каталог
WORKDIR /app

# Выполняем команду для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]