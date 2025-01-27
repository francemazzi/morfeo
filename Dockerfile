FROM python:3.11.7-slim

# Add timeout settings for apt
RUN echo 'Acquire::http::Timeout "240";' > /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::ftp::Timeout "240";' >> /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::https::Timeout "240";' >> /etc/apt/apt.conf.d/99timeout

# Install system dependencies for Linux with retries
RUN --mount=type=cache,target=/var/cache/apt \
    for i in {1..3}; do \
    apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    build-essential \
    python3-dev \
    libpython3-dev \
    pkg-config \
    libcairo2-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/* && break || sleep 30; \
    done

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_DEFAULT_TIMEOUT=100

COPY requirements.txt .

# Install base Python packages with retry and longer timeout
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in {1..3}; do \
        pip install --upgrade pip --timeout 100 && \
        pip install --timeout 100 \
        fastapi>=0.109.0 \
        uvicorn==0.24.0 \
        python-dotenv==1.0.0 \
        python-multipart==0.0.6 \
        beautifulsoup4>=4.12.0 \
        lxml>=4.9.0 \
        aiohttp>=3.9.0 && break || sleep 30; \
    done

# Install ML and data processing packages with retry
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in {1..3}; do \
        pip install --timeout 100 \
        pandas==2.1.3 \
        pdf2image==1.16.3 \
        pytesseract==0.3.10 \
        opencv-python==4.8.1.78 \
        Pillow>=10.0.0 \
        PyMuPDF==1.23.8 \
        requests>=2.31.0 && break || sleep 30; \
    done

# Install Pydantic with retry
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in {1..3}; do \
        pip install --timeout 100 \
        "pydantic>=2.5.2,<3.0.0" \
        "pydantic-settings>=2.1.0" && break || sleep 30; \
    done

# Install LangChain packages with retry
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in {1..3}; do \
        pip install --timeout 100 \
        langchain-core>=0.3.31 \
        langchain-community>=0.3.15 \
        langchain-openai>=0.0.5 \
        langchain-huggingface>=0.1.2 && break || sleep 30; \
    done

# Install Hugging Face packages with retry
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in {1..3}; do \
        pip install --timeout 100 \
        "transformers>=4.38.2,<4.49.0" \
        torch==2.2.1 \
        sentencepiece>=0.1.99 \
        accelerate>=0.27.0 \
        scikit-learn>=1.6.1 \
        scipy>=1.15.1 \
        sentence-transformers>=2.2.2 && break || sleep 30; \
    done

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

COPY --chown=appuser:appuser app/ app/
COPY --chown=appuser:appuser alembic.ini .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]