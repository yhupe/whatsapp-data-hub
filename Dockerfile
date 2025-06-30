# Dockerfile

# Step 1 : Build environment
FROM python:3.11-slim-bookworm AS builder

# Set environment variables for Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set working directory in container
WORKDIR /app

# Install system dependencies needed for psycopg2-binary (PostgreSQL-adapterdapter)
# libpq-dev is important for postgre linking
# build-essential und gcc are for compiling of Python-Packages with C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# copy the requirements.txt into the container
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Sep 2: Runtime environment
FROM python:3.11-slim-bookworm

# set working directory again
WORKDIR /app

# copying the installed Python-Packages from 'builder'-Step
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# copying the rest from application code into the container
COPY . /app

# set the port on which the app will run (FastAPI/Uvicorn Standard)
EXPOSE 8000

# Define the command that will be called when starting the container
# This command starts the FastAPI app with Gunicorn and Uvicorn-Workern
# 'main:app' means that the  FastAPI instance 'app' is located in file 'main.py'

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]