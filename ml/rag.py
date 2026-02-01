from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os
import requests

# =============================
# CONFIG
# =============================

LLM_MODE = os.getenv("LLM_MODE", "offline")  
# offline | openai | ollama

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_URL = "http://localhost:11434/api/generate"

# =============================
# INIT
# =============================

model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.Client(
    Settings(
        persist_directory="./ml/data",
        anonymized_telemetry=False
    )
)

collection = chroma_client.get_or_create_collection(name="documents")

# =============================
# PDF INGESTION
# =============================

def ingest_pdf(file_path: str):
    reader = PdfReader(file_path)

    chunks = []
    metadatas = []
    chunk_size = 500
    overlap = 50

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue

        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
            metadatas.append({
                "source": os.path.basename(file_path),
                "page": page_number + 1
            })

    embeddings = model.encode(chunks).tolist()

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=[f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
    )

# =============================
# LLM CALLS
# =============================

def call_openai(prompt: str) -> str:
    import openai
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es un assistant qui répond précisément à partir du contexte fourni."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def call_ollama(prompt: str) -> str:
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    return response.json()["response"]

# =============================
# RAG
# =============================

def answer_question(question: str) -> str:
    if collection.count() == 0:
        return "Aucun document indexé."

    query_embedding = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )

    context_blocks = []
    sources = set()

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context_blocks.append(f"- {doc}")
        sources.add(f'{meta["source"]} (page {meta["page"]})')

    context = "\n".join(context_blocks)

    prompt = f"""
Voici des extraits de documents :

{context}

Question :
{question}

Tâche :
- Réponds clairement
- Fais un résumé intelligent
- Ne réponds QUE si l'information est dans le contexte
"""

    if LLM_MODE == "openai" and OPENAI_API_KEY:
        answer = call_openai(prompt)
    elif LLM_MODE == "ollama":
        answer = call_ollama(prompt)
    else:
        # fallback offline
        answer = context[:800]

    sources_text = "\n".join(sources)
    return f"{answer}\n\nSources :\n{sources_text}"
