from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, HTTPException
import shutil
import os

from pydantic import BaseModel
from src.document_processor.pdf_parser import PDFParser
from database import SessionLocal, Document

# Créer l'application FastAPI
app = FastAPI(title="Chatbot RAG Backend")

# Ajouter CORS pour permettre au frontend Streamlit d'appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # autorise toutes les origines
    allow_methods=["*"],
    allow_headers=["*"]
)

# Endpoint racine
@app.get("/")
def root():
    return {"message": "Backend is running"}

# Endpoint health
@app.get("/health")
def health():
    return {"status": "ok"}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

pdf_parser = PDFParser()

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    pdf_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save PDF
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract
    metadata = pdf_parser.extract_metadata(pdf_path)
    text = pdf_parser.extract_text(pdf_path)

    # Save extracted text
    text_filename = file.filename.replace(".pdf", ".txt")
    text_path = os.path.join(UPLOAD_DIR, text_filename)

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Store in DB
    db = SessionLocal()
    doc = Document(
        filename=file.filename,
        pdf_path=pdf_path,
        text_path=text_path
    )
    db.add(doc)
    db.commit()
    db.close()

    return {
        "message": "PDF uploaded and indexed",
        "filename": file.filename,
        "pages": metadata.get("num_pages"),
        "text_file": text_filename
    }


class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_question(q: Question):
    # For now, just a placeholder
    return {"answer": "RAG pipeline not ready yet"}