# Use Python 3.12 slim version
FROM python:3.12-slim

# Prevents Python from writing pyc files & enables unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all files into container
COPY . .

# Run migrations, create superuser, and start server
CMD ["sh", "-c", "\
    python manage.py migrate && \
    python manage.py shell -c \"\
from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='ridhi').exists() or \
User.objects.create_superuser('ridhi', 'ridhi@gmail.com', 'ridhi')\" && \
    python manage.py runserver 0.0.0.0:8000 \
"]
