FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/rightOnTime

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rightOnTime/ .

ENV DJANGO_SETTINGS_MODULE=rightOnTime.settings

EXPOSE 8000

CMD ["gunicorn", "rightOnTime.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3"]
