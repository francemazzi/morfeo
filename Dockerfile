FROM python:3.11-slim

WORKDIR /app

# Installo le dipendenze di sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    swig \
    tesseract-ocr \
    poppler-utils \
    python3-poppler \
    python3-poppler-qt5 \
    libpoppler-cpp-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 