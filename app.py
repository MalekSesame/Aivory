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
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Sauvegarde du PDF
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extraire metadata et texte
    metadata = pdf_parser.extract_metadata(file_path)
    text = pdf_parser.extract_text(file_path)

    # Stocker le nom du fichier dans SQLite
    db = SessionLocal()
    doc = Document(filename=file.filename)
    db.add(doc)
    db.commit()
    db.close()

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "metadata": metadata,
        "text_preview": text[:200]  # juste un aperçu du texte
    }

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_question(q: Question):
    # For now, just a placeholder
    return {"answer": "RAG pipeline not ready yet"}