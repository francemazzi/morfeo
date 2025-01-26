# Morfeo - AI-Powered Medical Report Analyzer

<div align="center">

![Morfeo server image](./.github/assets/morfeo.jpg)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![GPT](https://img.shields.io/badge/GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFAC2F?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co)

Morfeo is a powerful microservice designed to extract and analyze medical laboratory reports using state-of-the-art AI technology. By combining GPT capabilities with Hugging Face models and advanced OCR processing, Morfeo can accurately identify, extract, and structure medical data from PDF documents and images.

</div>

## ✨ Key Features

- 📊 **Medical Data Structuring**: Converts medical reports into clean, standardized JSON format
- 🎯 **Specialized Medical Analysis**: Focused on laboratory test results and reference ranges
- 🔄 **Format Standardization**: Automatically converts numerical formats (e.g., comma to dot in decimals)
- 🚀 **High Performance**: Processes documents quickly with optimized image processing
- 🌐 **RESTful API**: Simple and intuitive API endpoints

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Langchain**: Framework for building LLM applications
- **PDF2Image**: PDF to image conversion
- **Docker**: Containerization for easy deployment
- **Pydantic**: Data validation using Python type annotations

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API Key
- Hugging Face API Token
- Python 3.11+

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
   OPENAI_API_KEY=your_openai_api_key
   HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
   ```

3. Install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run with Docker:
   ```bash
   docker-compose up -d
   ```
   Or locally:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🎮 Usage

### Extract Medical Data from PDF/Images

```bash
curl -X POST "http://localhost:8000/api/v1/extract-medical-data" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@report.pdf"
```

### Extract Tables Only

```bash
curl -X POST "http://localhost:8000/api/v1/extract-tables" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@report.pdf"
```

## 📁 Project Structure

```
.
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── data_extraction.py
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   ├── ocr_service.py
│   │   └── structure_data_service.py
│   └── main.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔧 Architecture

The system works in three main steps:

1. **Document Processing**

   - PDF to image conversion
   - High-quality image extraction (800 DPI)

2. **Data Extraction**

   - Table structure recognition with GPT-4o
   - Text extraction and formatting

3. **Medical Data Analysis**
   - Medical field identification
   - Reference range parsing
   - Unit standardization

## 📋 TODO & Future Improvements

1. **Prompt Customization System**

   - Implement user interface for custom prompt input
   - Create a collection system for effective prompts
   - Build a training dataset from the first 10-20 users' interactions
   - 📝 **Smart OCR**: Enhanced OCR capabilities with Tesseract

2. **Entity Management**

   - Add entity management system (e.g., "Pie APC")
   - Implement custom entity parser
   - Create entity mapping database

3. **Advanced Optimizations**

   - Integrate AGRF agent for Lumin Thinking control
   - Enhance result validation system
   - Implement continuous learning feedback system

4. **Architectural Improvements**

   - Optimize document processing flow
   - Implement caching system for frequent requests
   - Improve error handling and recovery

5. **Data Collection and Analysis**
   - Implement performance tracking system
   - Create results analysis dashboard
   - Optimize models based on collected data

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](../../issues).
