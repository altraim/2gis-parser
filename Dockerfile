# Используем официальный образ Python с нужной версией
FROM mcr.microsoft.com/playwright/python:v1.53.0-noble

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Playwright и его зависимости
RUN playwright install

# Создаем рабочую директорию
WORKDIR /parser

# Копируем исходный код
COPY . .

# Команда для запуска
CMD ["python", "main.py"]