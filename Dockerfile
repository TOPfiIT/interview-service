# Используем multiarch образ Python
FROM --platform=$BUILDPLATFORM python:3.13-slim

WORKDIR /app

# Устанавливаем системные зависимости, необходимые для сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
RUN pip install --no-cache-dir uv

# Копируем файлы зависимостей
COPY requirements.txt ./

# Устанавливаем зависимости
RUN uv pip install --system -r requirements.txt

# Копируем исходный код приложения
COPY ./src ./src

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
