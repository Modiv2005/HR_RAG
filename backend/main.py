from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import rag_pipeline

app = FastAPI(title="HR Policy RAG Assistant")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list

@app.post("/upload-doc")
async def upload_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        num_chunks = rag_pipeline.ingest_document(contents, file.filename)
        return {"message": f"Successfully processed {file.filename}. Created {num_chunks} chunks."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_assistant(request: QueryRequest):
    try:
        # Retrieve context
        context_chunks = rag_pipeline.retrieve_context(request.query)
        
        # Format sources
        sources = []
        for chunk in context_chunks:
            sources.append({
                "source": chunk["metadata"]["source"],
                "text": chunk["metadata"]["text"],
                "score": chunk["score"]
            })
            
        # Generate answer
        answer = rag_pipeline.generate_answer(request.query, context_chunks)
        
        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/retrieve")
async def retrieve_test(query: str):
    """Utility endpoint to test retrieval logic independently."""
    try:
        context_chunks = rag_pipeline.retrieve_context(query)
        return {"results": context_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
