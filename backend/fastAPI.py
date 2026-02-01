"""
FastAPI server for Aviory RAG Pipeline
Provides REST API endpoints for document Q&A
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from rag_pipeline import RAGPipeline

# Initialize FastAPI app
app = FastAPI(
    title="Aviory API",
    description="REST API for document Q&A using RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5

class SourceDocument(BaseModel):
    text: str
    source: str
    relevance: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceDocument]

class StatusResponse(BaseModel):
    documents_loaded: bool
    num_chunks: int
    documents_folder: str
    model: str

class ReloadRequest(BaseModel):
    documents_folder: Optional[str] = "documents"

# Global state
class AppState:
    def __init__(self):
        self.vector_store = None
        self.rag_pipeline = None
        self.documents_loaded = False
        self.num_chunks = 0
        self.documents_folder = "./documents"
        self.processor = None

state = AppState()

def initialize_documents(folder: str = "documents"):
    """Initialize documents and RAG pipeline"""
    try:
        state.documents_folder = folder
        state.processor = DocumentProcessor(folder)
        documents = state.processor.load_documents()
        
        if not documents:
            raise ValueError(f"No documents found in {folder}")
        
        chunks = state.processor.split_documents(documents)
        
        docs_for_vector_store = []
        for i, chunk in enumerate(chunks):
            docs_for_vector_store.append({
                "text": chunk.page_content,
                "metadata": {
                    "source": chunk.metadata.get("source", f"chunk_{i}"),
                    "page": chunk.metadata.get("page", 0)
                }
            })
        
        state.vector_store = VectorStoreManager()
        state.vector_store.add_documents(docs_for_vector_store)
        state.num_chunks = len(chunks)
        
        # Initialize RAG pipeline
        try:
            state.rag_pipeline = RAGPipeline("llama-3")
        except Exception as e:
            print(f"Warning: RAG pipeline initialization failed: {e}")
            state.rag_pipeline = RAGPipeline("small")
        
        state.documents_loaded = True
        print(f"✅ Successfully loaded {state.num_chunks} chunks from {folder}")
        
    except Exception as e:
        state.documents_loaded = False
        print(f"❌ Error loading documents: {e}")
        raise

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize documents on startup"""
    try:
        initialize_documents()
    except Exception as e:
        print(f"Warning: Could not initialize documents on startup: {e}")

@app.get("/", tags=["Info"])
async def root():
    """API root endpoint"""
    return {
        "name": "Aviory API",
        "version": "1.0.0",
        "description": "REST API for document Q&A using RAG",
        "docs": "/docs"
    }

@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status():
    """Get API status and system information"""
    return StatusResponse(
        documents_loaded=state.documents_loaded,
        num_chunks=state.num_chunks,
        documents_folder=state.documents_folder,
        model="lightweight-extractive"
    )

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_documents(request: QueryRequest):
    """
    Query documents and get answers using RAG
    
    - **question**: The question to ask
    - **top_k**: Number of source documents to retrieve (default: 5)
    """
    if not state.documents_loaded:
        raise HTTPException(
            status_code=400,
            detail="Documents not loaded. Please reload documents first."
        )
    
    if not state.rag_pipeline:
        raise HTTPException(
            status_code=500,
            detail="RAG pipeline not initialized."
        )
    
    try:
        # Search for relevant documents
        retrieved_docs = state.vector_store.similarity_search(
            request.question,
            k=request.top_k
        )
        
        # Generate answer
        result = state.rag_pipeline.query(request.question, retrieved_docs)
        
        # Format response
        sources = [
            SourceDocument(
                text=source["text"][:300],
                source=source["metadata"].get("source", "Unknown"),
                relevance=float(1 - source["distance"])
            )
            for source in result["sources"]
        ]
        
        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            sources=sources
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.post("/documents/reload", tags=["Documents"])
async def reload_documents(request: ReloadRequest):
    """
    Reload documents from specified folder
    
    - **documents_folder**: Path to folder containing documents (default: "documents")
    """
    try:
        initialize_documents(request.documents_folder)
        return {
            "status": "success",
            "message": f"Successfully loaded {state.num_chunks} chunks",
            "documents_folder": state.documents_folder,
            "num_chunks": state.num_chunks
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reloading documents: {str(e)}"
        )

@app.get("/documents/info", tags=["Documents"])
async def get_documents_info():
    """Get information about loaded documents"""
    if not state.documents_loaded:
        raise HTTPException(
            status_code=400,
            detail="No documents loaded"
        )
    
    return {
        "documents_folder": state.documents_folder,
        "num_chunks": state.num_chunks,
        "model": "lightweight-extractive"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "documents_loaded": state.documents_loaded,
        "num_chunks": state.num_chunks
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
