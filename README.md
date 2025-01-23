# Morfeo - AI-Powered PDF Table Extractor

<div align="center">
![Morfeo server image](./.github/assets/morfeo.jpg)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![GPT-4](https://img.shields.io/badge/GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)

Morfeo is a powerful microservice designed to extract and analyze tables from PDF documents using cutting-edge AI technology. By combining llm Vision capabilities with advanced image processing, Morfeo can accurately identify, extract, and structure tabular data from any PDF document.

</div>

## ✨ Key Features

- 🔍 **Intelligent Table Detection**: Uses GPT-4 Vision to identify and extract tables with high accuracy
- 📊 **Structured Data Output**: Converts PDF tables into clean, structured JSON format
- 🚀 **High Performance**: Processes PDFs quickly and efficiently
- 🔄 **RESTful API**: Simple and intuitive API endpoints
- 📦 **Containerized**: Easy deployment with Docker
- 📧 **Email Integration**: Built-in email notifications with MailHog
- 🗄️ **Persistent Storage**: Automatic storage in PostgreSQL database

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust database for storing extraction results
- **SQLAlchemy**: Powerful SQL toolkit and ORM
- **GPT-4 Vision**: State-of-the-art AI for visual data extraction
- **Docker**: Containerization for easy deployment
- **Pydantic**: Data validation using Python type annotations
- **MailHog**: Email testing tool for development

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API Key
- Unstructured API Key

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/morfeo.git
   cd morfeo
   ```

2. Configure environment variables:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your API keys:

   ```
   DATABASE_URL=postgresql://postgres:postgres@db:5432/pdf_extractor
   MAILHOG_HOST=mailhog
   MAILHOG_PORT=1025
   UNSTRUCTURED_API_KEY=your_unstructured_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

## 🎮 Usage

### Extract Tables from PDF

```bash
curl -X POST "http://localhost:8000/api/v1/pdf/extract/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Get All Extractions

```bash
curl -X GET "http://localhost:8000/api/v1/pdf/extractions/" \
  -H "accept: application/json"
```

### Get Specific Extraction

```bash
curl -X GET "http://localhost:8000/api/v1/pdf/extraction/1" \
  -H "accept: application/json"
```

## 🌐 Services

- **API**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MailHog UI**: [http://localhost:8025](http://localhost:8025)
- **PostgreSQL**: localhost:5432

## 📁 Project Structure

```
.
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── pdf.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   └── pdf.py
│   ├── schemas/
│   │   └── pdf.py
│   ├── services/
│   │   └── pdf_service.py
│   └── main.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## How to run the project

Step 1:

```
python -m venv venv
```

Step 2:

```
source venv/bin/activate
```

Step 3:

```
pip install -r requirements.txt

```

## How to run the server

```

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](../../issues).
