import os
import io
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from openai import OpenAI

# Initialize local embedding model
# all-MiniLM-L6-v2 is fast and efficient for standard semantic search
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
VECTOR_DIMENSION = 384  # MiniLM-L6-v2 outputs 384-dimensional vectors

INDEX_FILE = "faiss_index.bin"
METADATA_FILE = "faiss_metadata.json"

# In-memory stores
index = None
chunks_metadata = []

def init_index():
    global index, chunks_metadata
    if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(METADATA_FILE, "r") as f:
            chunks_metadata = json.load(f)
    else:
        index = faiss.IndexFlatL2(VECTOR_DIMENSION)
        chunks_metadata = []

# Call init_index on load
init_index()

def save_index():
    faiss.write_index(index, INDEX_FILE)
    with open(METADATA_FILE, "w") as f:
        json.dump(chunks_metadata, f)

def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    text = ""
    
    if ext == "pdf":
        text = extract_pdf_text(io.BytesIO(file_bytes))
    elif ext in ["doc", "docx"]:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([p.text for p in doc.paragraphs])
    elif ext == "txt":
        text = file_bytes.decode("utf-8")
    else:
        raise ValueError("Unsupported file format.")
    
    return text

def ingest_document(file_bytes: bytes, filename: str):
    global index, chunks_metadata
    
    # 1. Extract text
    text = extract_text(file_bytes, filename)
    
    if not text.strip():
        raise ValueError("No text could be extracted from the document.")
        
    # 2. Chunk text intelligently
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    
    if not chunks:
        return 0
        
    # 3. Generate embeddings
    embeddings = embedder.encode(chunks, convert_to_numpy=True)
    
    # 4. Store in FAISS
    index.add(embeddings)
    
    # 5. Store metadata
    for i, chunk in enumerate(chunks):
        chunks_metadata.append({
            "source": filename,
            "text": chunk,
            "chunk_index": i
        })
        
    save_index()
    return len(chunks)

def retrieve_context(query: str, top_k: int = 3):
    if index.ntotal == 0:
        return []
        
    query_embedding = embedder.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx != -1 and idx < len(chunks_metadata):
            results.append({
                "score": float(dist),
                "metadata": chunks_metadata[idx]
            })
            
    return results

def generate_answer(query: str, context_chunks: list) -> str:
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        return "[SYSTEM ERROR]: OPENAI_API_KEY environment variable is not set. Cannot generate an answer."
        
    client = OpenAI(api_key=openai_key)
    
    if not context_chunks:
        return "This information is not available in the company HR policy documents."
        
    # Combine chunks into a single string
    context_text = "\n\n".join([f"--- Source: {c['metadata']['source']} ---\n{c['metadata']['text']}" for c in context_chunks])
    
    prompt = f"""You are an HR policy assistant. Answer ONLY using the provided company HR documents.
Do not assume or generate information.
If the answer is not present, say it is unavailable.

Context:
{context_text}

Employee Question:
{query}

Answer:"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strict, document-grounded HR assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with LLM: {str(e)}"
