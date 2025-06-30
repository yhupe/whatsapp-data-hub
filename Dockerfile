# Dockerfile


FROM python:3.11-bookworm


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    gcc \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . /app


EXPOSE 8000


ENTRYPOINT ["/usr/local/bin/gunicorn"]


CMD ["python", "-c", "import sys; print('Python is running! sys.version:', sys.version); print('sys.path:', sys.path);"]