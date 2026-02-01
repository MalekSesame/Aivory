from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
from pydantic import BaseModel

from backend.database import init_db, insert_document
from ml.rag import ingest_pdf, answer_question

# =============================
# CONFIG
# =============================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Mini RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# STARTUP
# =============================

@app.on_event("startup")
def startup():
    init_db()

# =============================
# HEALTH CHECK
# =============================

@app.get("/health")
def health():
    return {"status": "ok"}

# =============================
# PDF UPLOAD + INDEXATION
# =============================

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Sauvegarde + ingestion RAG
    insert_document(file.filename, str(file_path))
    ingest_pdf(str(file_path))

    return {"message": "PDF uploaded and indexed successfully"}

# =============================
# QUESTION / RAG
# =============================

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    answer = answer_question(request.question)
    return {"answer": answer}
