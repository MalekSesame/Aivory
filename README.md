# Aviory - Document Q&A Assistant

Une application intelligente pour explorer vos documents avec des questions naturelles utilisant RAG (Retrieval-Augmented Generation).

## Fonctionnalités

- Interface Streamlit intuitive pour poser des questions
- Recherche sémantique dans vos documents
- Support PDF et fichiers texte
- Pipeline RAG léger et rapide
- API REST FastAPI pour intégration
- Gestion automatique des documents

##  Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)

##  Installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

3. **Préparer les documents**

Créez un dossier `documents/` et ajoutez vos fichiers:
```
documents/
  ├── file1.pdf
  ├── file2.txt
  └── file3.pdf
```

## ▶ Lancer l'application

### Option 1: Streamlit (Interface Web)

```bash
streamlit run app.py
```

L'application s'ouvrira à `http://localhost:8501`

### Option 2: FastAPI (API REST)

```bash
python api.py
```

ou avec uvicorn directement:

```bash
uvicorn api:app --reload
```

L'API sera disponible à:
- **API**: `http://localhost:8000`
- **Documentation interactive**: `http://localhost:8000/docs`
- **Alternative Swagger**: `http://localhost:8000/redoc`

### Option 3: Lancer les deux simultanément

**Terminal 1 - Streamlit:**
```bash
streamlit run app.py
```

**Terminal 2 - FastAPI:**
```bash
python api.py
```

## API Endpoints

### Endpoints disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Information sur l'API |
| GET | `/health` | Vérification de santé |
| GET | `/status` | État du système |
| POST | `/query` | Poser une question |
| POST | `/documents/reload` | Recharger les documents |
| GET | `/documents/info` | Info sur les documents |

### Exemple d'utilisation de l'API

**Poser une question:**

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qu'est-ce que c'est?",
    "top_k": 5
  }'
```

**Obtenir le statut:**

```bash
curl "http://localhost:8000/status"
```

**Recharger les documents:**

```bash
curl -X POST "http://localhost:8000/documents/reload" \
  -H "Content-Type: application/json" \
  -d '{
    "documents_folder": "documents"
  }'
```

### Réponse typique

```json
{
  "question": "Qu'est-ce que c'est?",
  "answer": "C'est une réponse basée sur vos documents...",
  "sources": [
    {
      "text": "Extrait du document...",
      "source": "file.pdf",
      "relevance": 0.95
    }
  ]
}
```

## Architecture

```
Aviory/
├── app.py                    # Application Streamlit (UI)
├── api.py                    # Serveur FastAPI (API REST)
├── styles.py                 # Styles et CSS
├── document_processor.py      # Traitement des documents
├── vector_store.py           # Gestion des embeddings
├── rag_pipeline.py           # Pipeline RAG
├── requirements.txt          # Dépendances
├── documents/                # Dossier avec vos documents
└── chroma_db/               # Base de données vectorielle
```

## Modules

- **document_processor.py**: Charge et divise les documents en chunks
- **vector_store.py**: Gère les embeddings avec ChromaDB
- **rag_pipeline.py**: Pipeline RAG pour générer les réponses
- **styles.py**: Définitions CSS/styling
- **app.py**: Interface Streamlit
- **api.py**: Serveur FastAPI REST

## Configuration

Les chemins et paramètres par défaut:

```python
documents_folder = "documents"    # Dossier des documents
top_k = 5                         # Nombre de sources retournées
chunk_size = 1000                 # Taille des chunks
chunk_overlap = 200               # Chevauchement entre chunks
```

## Variables d'environnement 

Créez un fichier `.env`:

```env
DOCUMENTS_FOLDER=documents
TOP_K=5
```

##  Technologies

- **Streamlit**: Framework web Python
- **FastAPI**: Framework API REST moderne
- **LangChain**: Orchestration RAG
- **ChromaDB**: Base vectorielle
- **Sentence-Transformers**: Embeddings
- **PyPDF**: Traitement PDF

##  Documentation API

Accédez à la documentation interactive:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

##  Cas d'usage

- Recherche dans des rapports d'entreprise
- Questions sur des documents techniques
- Assistance à la recherche documentaire
- Chatbot basé sur votre documentation

##  Roadmap

- [ ] Support pour plus de formats (Word, Excel)
- [ ] Interface d'authentification
- [ ] Stockage multi-utilisateurs
- [ ] Export des réponses (PDF, DOCX)
- [ ] Support des images/OCR
- [ ] Modèles LLM plus puissants

