# 🤖 AI-Powered HR Policy RAG Assistant

An intelligent, full-stack Retrieval-Augmented Generation (RAG) chatbot that answers employee queries **strictly** based on uploaded HR policy documents. It avoids hallucinations by grounding all responses in retrieved document content.

---

## 📁 Folder Structure

```
hr-rag-assistant/
├── backend/
│   ├── venv/                  # Python virtual environment
│   ├── main.py                # FastAPI app with API endpoints
│   ├── rag_pipeline.py        # Core RAG logic (ingestion, retrieval, generation)
│   ├── requirements.txt       # Python dependencies
│   ├── faiss_index.bin         # Persisted FAISS vector index (auto-generated)
│   └── faiss_metadata.json    # Chunk metadata store (auto-generated)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css    # Premium glassmorphism styling
│   │   │   ├── layout.js      # Root layout with SEO metadata
│   │   │   └── page.jsx       # Main dashboard page
│   │   └── components/
│   │       ├── AdminUpload.jsx    # HR Admin document upload component
│   │       └── ChatInterface.jsx  # Employee query chat component
│   ├── package.json
│   └── ...
├── sample_leave_policy.txt    # Sample test document
├── sample_payroll_policy.txt  # Sample test document
└── README.md                 # This file
```

---

## ⚙️ Tech Stack

| Layer       | Technology                       |
|-------------|----------------------------------|
| Frontend    | Next.js 16 (React), Vanilla CSS  |
| Backend     | Python 3, FastAPI, Uvicorn       |
| Vector DB   | FAISS (faiss-cpu)                |
| Embeddings  | Sentence Transformers (all-MiniLM-L6-v2) |
| LLM         | OpenAI GPT-3.5-turbo             |
| Doc Parsing | pdfminer.six, python-docx        |
| Chunking    | LangChain RecursiveCharacterTextSplitter |

---

## 🚀 Setup & Run (Local)

### Prerequisites
- Python 3.9+
- Node.js 18+
- An OpenAI API Key

### 1. Backend Setup

```bash
cd hr-rag-assistant/backend

# Create virtual environment (already done if you cloned)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`.

### 2. Frontend Setup

```bash
cd hr-rag-assistant/frontend

# Install dependencies (already done if you cloned)
npm install

# Start the dev server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

---

## 📡 API Endpoints

| Method | Endpoint       | Description                                  |
|--------|----------------|----------------------------------------------|
| POST   | `/upload-doc`  | Upload an HR document (PDF, DOCX, TXT)       |
| POST   | `/query`       | Ask a question, get a document-grounded answer |
| GET    | `/retrieve`    | Test semantic retrieval independently        |

### Example: Upload a Document
```bash
curl -X POST -F "file=@sample_leave_policy.txt" http://localhost:8000/upload-doc
```

### Example: Query the Assistant
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many casual leaves are allowed?"}'
```

### Example: Test Retrieval
```bash
curl "http://localhost:8000/retrieve?query=salary+payment+cycle"
```

---

## 🧪 Test Cases

| # | Action                                 | Expected Result                                         |
|---|----------------------------------------|---------------------------------------------------------|
| 1 | Upload `sample_leave_policy.txt`       | "Successfully processed... Created N chunks."           |
| 2 | Ask: "How many casual leaves allowed?" | "12 casual leaves per calendar year" (from policy)      |
| 3 | Upload `sample_payroll_policy.txt`     | "Successfully processed... Created N chunks."           |
| 4 | Ask: "What is the salary payment cycle?" | "Last working day of every month" (from policy)       |
| 5 | Ask: "What is the stock price?"        | "This information is not available in the company HR policy documents." |

---

## 🔒 Security & Access Control

- **HR Admin**: Can upload and manage policy documents via the left panel
- **Employees**: Can only query via the chat interface on the right panel
- **Document Storage**: FAISS index files are stored server-side only
- **Strict RAG**: The LLM is prompted to NEVER generate information outside the retrieved context

---

## 🎨 Design Features

- **Glassmorphism UI** with frosted-glass panels and backdrop blur
- **Gradient color palette** (indigo → purple → pink accents)
- **Smooth micro-animations** on messages and hover effects
- **Responsive layout** that adapts from desktop to mobile
- **Source citations** with relevance scores shown alongside answers

---

## ☁️ Deployment (Cloud)

### Docker (Recommended)
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Platforms
- **Backend**: Deploy to AWS EC2, Google Cloud Run, or Railway
- **Frontend**: Deploy to Vercel (optimal for Next.js)
- **Environment**: Set `OPENAI_API_KEY` as an environment variable in your cloud provider

---

## 📌 Constraints

- ✅ **No hallucination** — strict prompt engineering ensures document-only answers
- ✅ **High accuracy** — semantic search with sentence-transformers
- ✅ **Fast retrieval** — FAISS provides sub-second vector search
