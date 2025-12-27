# DocumentQA

A simple **Document Question Answering (QA)** backend built with **Django**, **TF-IDF retrieval**, and **LangChain + HuggingFace LLM**.

This project is intentionally designed for a **Junior Backend Developer interview task**: the focus is on clean architecture, understandable data flow, and explainable technical decisions — not over-engineering.

---

## ✨ Features

- Upload and manage documents via Django Admin
- Retrieve relevant documents using **TF-IDF + cosine similarity**
- Generate answers using **LangChain** connected to a **HuggingFace LLM**
- Clean separation of concerns (views / services / retrieval / LLM)
- REST-style API endpoints
- Docker & local development support

---

## 🧱 High-Level Architecture

```
User Question
    ↓
API View (documents/views.py)
    ↓
Retrieval Service (documents/services/retriever.py)
    ↓
TF-IDF Similarity Search
    ↓
Context Builder
    ↓
QA Chain (documents/services/qa_chain.py)
    ↓
HuggingFace LLM (via LangChain)
    ↓
Answer Returned to User
```

---

## 📁 Project Structure

```
DocumentQA/
│
├── docqa_project/        # Django settings & URLs
├── documents/            # Main application
│   ├── models.py         # Document model
│   ├── views.py          # API views
│   ├── services/
│   │   ├── retriever.py  # TF-IDF retrieval logic
│   │   └── qa_chain.py   # LangChain + LLM integration
│
├── manage.py
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 🚀 Running the Project (Local)

### 1️⃣ Prerequisites

- Python **3.10+**
- pip
- virtualenv (recommended)

---

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/hadikh97/DocumentQA.git
cd DocumentQA
```

---

### 3️⃣ Create & Activate Virtual Environment

**Windows (PowerShell):**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=django-secret-key
USE_FAKE_LLM=False
HUGGINGFACE_MODEL=google/flan-t5-base
```

> `USE_FAKE_LLM=True` can be used for testing without calling a real model.

---

### 6️⃣ Apply Migrations & Create Superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

### 7️⃣ Run the Server

```bash
python manage.py runserver
```

- Admin panel: http://127.0.0.1:8000/admin/
- API base: http://127.0.0.1:8000/api/

---

## 🧪 API Usage Examples

### 🔹 Retrieve Relevant Documents

```bash
curl -X POST http://127.0.0.1:8000/api/retrieve/ \
     -H "Content-Type: application/json" \
     -d '{"query": "What is Django?"}'
```

---

### 🔹 Ask a Question (Full QA Flow)

```bash
curl -X POST http://127.0.0.1:8000/api/ask/ \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Django used for?"}'
```

**Response example:**
```json
{
  "question": "What is Django used for?",
  "answer": "Django is a high-level Python web framework used for building web applications.",
  "documents_used": [
    {"id": 1, "title": "Django Overview"}
  ]
}
```

---

## 🤖 LLM Integration Details

- LLM integration lives in:
  ```
  documents/services/qa_chain.py
  ```

- Uses **LangChain** to:
  - Build prompt
  - Inject retrieved document context
  - Call HuggingFace model

- Switching between fake and real LLM is controlled via:
  ```env
  USE_FAKE_LLM=True | False
  ```

---

## 🧠 Why TF-IDF (Design Decision)

For a junior-level backend task:

- TF-IDF is:
  - Simple
  - Fast
  - Easy to explain
- Demonstrates understanding of **retrieval pipelines**

> Embedding-based semantic search can be added later for production-scale systems.

---

## 🐳 Running with Docker (Optional)

```bash
docker-compose up --build
```

---

## ⚠️ Notes for Interviewers

- Project intentionally avoids over-engineering
- Focus is on:
  - Clean backend structure
  - Retrieval + LLM integration
  - Explainable decisions

---

## 📌 Future Improvements (Out of Scope)

- Semantic search with embeddings
- Caching (Redis)
- Authentication
- Automated tests
- OpenAPI / Swagger docs

---

## 👤 Author

**Hadi Khodadadi**  
Backend Developer (Junior)

---

## 📄 License

MIT License

