# Document Question-Answering System

A Django backend system that manages textual documents, retrieves relevant content for user questions, and generates answers using LangChain with free LLMs.

## Features

- **Document Management**: Create, edit, delete, search, and filter documents via Django admin
- **Tag System**: Organize documents with multiple tags
- **TF-IDF Retrieval**: Find relevant documents using text similarity
- **LLM Integration**: Generate answers using HuggingFace models or FakeLLM for testing
- **REST API**: Full API for documents, questions, and answer generation
- **Docker Support**: Single-command deployment with PostgreSQL

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Django Application                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Admin     │  │  REST API   │  │      Models         │  │
│  │   Panel     │  │  Endpoints  │  │ Document/Tag/Question│ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│  ┌──────▼─────────────────▼─────────────────────▼──────────┐ │
│  │                    Services Layer                        │ │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ │ │
│  │  │ DocumentRetriever│    │      QAChainService         │ │ │
│  │  │   (TF-IDF)      │    │  (LangChain + HuggingFace)  │ │ │
│  │  └─────────────────┘    └─────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              │                               │
│  ┌───────────────────────────▼───────────────────────────┐   │
│  │              Storage Abstraction Layer                 │   │
│  │         (DatabaseStorageBackend / Future: S3)         │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │    PostgreSQL     │
                    └───────────────────┘
```

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/lebleuciel/chatservice.git
cd chatservice

# Start the application
docker-compose up --build

# In another terminal, load sample data
docker-compose exec web python manage.py load_samples
```

Access the application:
- **Admin Panel**: http://localhost:8000/admin (login: `admin`/`admin`)
- **API**: http://localhost:8000/api/

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export USE_FAKE_LLM=True

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py load_samples

# Run server
python manage.py runserver
```

## API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/documents/` | List all documents |
| GET | `/api/documents/{id}/` | Get document details |

### Questions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/questions/` | List all questions |
| POST | `/api/questions/` | Create a new question |
| GET | `/api/questions/{id}/` | Get question details |

### Retrieval & QA

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/retrieve/` | Find relevant documents |
| POST | `/api/ask/` | Ask question and get answer |
| POST | `/api/refresh-index/` | Refresh TF-IDF index |

### Example: Ask a Question

```bash
curl -X POST http://localhost:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the types of machine learning?"}'
```

Response:
```json
{
  "question_id": 1,
  "question": "What are the types of machine learning?",
  "answer": "Based on the provided documents...",
  "related_documents": [
    {"id": 1, "title": "Introduction to Machine Learning", "date": "2024-01-15"}
  ],
  "answered_at": "2024-02-10T12:00:00Z"
}
```

### Example: Retrieve Documents

```bash
curl -X POST http://localhost:8000/api/retrieve/ \
  -H "Content-Type: application/json" \
  -d '{"question": "cloud computing", "top_k": 3}'
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `True` | Django debug mode |
| `SECRET_KEY` | (generated) | Django secret key |
| `POSTGRES_DB` | `docqa` | Database name |
| `POSTGRES_USER` | `docqa` | Database user |
| `POSTGRES_PASSWORD` | `docqa` | Database password |
| `POSTGRES_HOST` | `db` | Database host |
| `USE_FAKE_LLM` | `True` | Use FakeLLM for testing |
| `HUGGINGFACE_MODEL` | `google/flan-t5-base` | HuggingFace model |
| `DOCUMENT_STORAGE_BACKEND` | `...DatabaseStorageBackend` | Storage backend |

### LLM Configuration

**FakeLLM (Testing)**:
```bash
USE_FAKE_LLM=True
```

**HuggingFace (Production)**:
```bash
USE_FAKE_LLM=False
HUGGINGFACE_MODEL=google/flan-t5-base
```

## Admin Panel Features

- **Documents**: Add, edit, delete with tag management
- **Questions**: View questions, generate answers
- **Admin Actions**:
  - "Refresh search index" - Rebuild TF-IDF index
  - "Find relevant documents" - Associate docs with questions
  - "Generate answers" - Generate LLM answers for questions

## Project Structure

```
chatservice/
├── docqa_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── documents/              # Main application
│   ├── models.py           # Document, Tag, Question models
│   ├── admin.py            # Admin configuration
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # URL routing
│   ├── services/
│   │   ├── retriever.py    # TF-IDF document retrieval
│   │   └── qa_chain.py     # LangChain QA service
│   ├── storage/
│   │   ├── base.py         # Storage interface
│   │   └── database.py     # Database storage backend
│   ├── fixtures/
│   │   └── sample_data.json
│   └── management/
│       └── commands/
│           └── load_samples.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Storage Backend

The system uses a storage abstraction layer for document content:

**Current**: `DatabaseStorageBackend` - Stores content in PostgreSQL TextField

**Future**: `ObjectStorageBackend` - Store in MinIO/S3 (not implemented)

To switch backends, change `DOCUMENT_STORAGE_BACKEND` in settings.

## Testing

```bash
# Run tests
python manage.py test documents

# With coverage
coverage run manage.py test documents
coverage report
```

## License

MIT License
