AI-Powered Knowledge Base Search & Enrichment

A comprehensive RAG (Retrieval-Augmented Generation) system that allows users to upload documents, search them using natural language, and get AI-powered answers with intelligent completeness checking and enrichment suggestions.

## Features

### Core Features
- **Document Upload & Storage**: Support for PDF, TXT, DOCX, XLSX, and CSV files
- **Natural Language Search**: Ask questions in plain language and get AI-generated answers
- **Intelligent Completeness Check**: AI detects when information is missing or uncertain
- **Enrichment Suggestions**: Suggests additional documents, data, or actions to fill knowledge gaps
- **Structured Output**: JSON responses with answer, confidence, missing_info, and enrichment suggestions

### Advanced Features
- **Confidence Scoring**: Three-level confidence system (High, Medium, Low)
- **Source Attribution**: Shows which documents and chunks were used for the answer
- **Answer Quality Rating**: Users can rate answers to improve the system
- **Real-time Processing**: Fast document processing and search
- **Modern Web Interface**: Responsive, user-friendly interface

### Stretch Goals
- **Auto-enrichment**: System can fetch missing data from external sources
- **Answer Quality Improvement**: Learning from user ratings to improve responses

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Wand_AI_Assesment2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Create necessary directories**
   ```bash
   mkdir uploads
   mkdir chroma_db
   ```

## Usage

1. **Start the application**
   ```bash
   python main.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:8000`

3. **Upload documents**
   - Drag and drop files or click to browse
   - Supported formats: PDF, TXT, DOCX, XLSX, CSV
   - Maximum file size: 10MB

4. **Search your knowledge base**
   - Type your question in natural language
   - Choose whether to include confidence analysis and enrichment suggestions
   - Get AI-powered answers with source attribution

5. **Rate answers**
   - Help improve the system by rating answer quality
   - Provide feedback for continuous improvement

## API Endpoints

### Document Management
- `POST /upload` - Upload a document
- `GET /documents` - List all uploaded documents
- `DELETE /documents/{filename}` - Delete a document

### Search
- `POST /search` - Search with form data
- `POST /search-json` - Search with JSON payload

### Analytics
- `POST /rate-answer` - Rate answer quality
- `GET /ratings` - Get all ratings
- `GET /stats` - Get system statistics
- `GET /health` - Health check

## Architecture

### Components
1. **Document Processor** (`document_processor.py`)
   - Handles file upload and text extraction
   - Manages vector database (ChromaDB)
   - Performs similarity search

2. **RAG Pipeline** (`rag_pipeline.py`)
   - Orchestrates search and answer generation
   - Implements completeness checking
   - Generates enrichment suggestions

3. **Web Application** (`main.py`)
   - FastAPI backend with REST endpoints
   - File upload handling
   - Response formatting

4. **Frontend** (`templates/`, `static/`)
   - Modern web interface
   - Real-time document processing
   - Interactive search and rating

### Technology Stack
- **Backend**: FastAPI, Python
- **AI/ML**: OpenAI GPT, Sentence Transformers, LangChain
- **Vector Database**: ChromaDB
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Document Processing**: PyPDF2, python-docx, openpyxl, pandas

## Configuration

Edit `config.py` to customize:
- File upload limits
- Chunk size and overlap
- Model settings
- Confidence thresholds
- Database settings

## Example Usage

### Upload Documents
```python
import requests

# Upload a PDF document
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload', files=files)
    print(response.json())
```


## Performance

- **Document Processing**: ~2-5 seconds per document (depending on size)
- **Search Response**: ~1-3 seconds per query
- **Concurrent Users**: Supports multiple simultaneous users
- **Storage**: Efficient vector storage with ChromaDB

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is set in the environment variables
   - Check that you have sufficient API credits

2. **File Upload Errors**
   - Verify file format is supported
   - Check file size is under 10MB
   - Ensure uploads directory exists

3. **Search Not Working**
   - Make sure documents are uploaded and processed
   - Check that ChromaDB is properly initialized
   - Verify OpenAI API key is working

### Debug Mode
Set environment variable for detailed logging:
```bash
export DEBUG=1
python main.py
