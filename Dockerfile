# Dockerfile

FROM python:3.11-slim-bookworm


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . /app


EXPOSE 8000


CMD ["python", "-c", "import sys; print(sys.path); from main import app; print('FastAPI app imported successfully!');"]