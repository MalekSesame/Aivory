from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()
collection = client.get_or_create_collection(name="documents")

def add_texts(texts: list[str]):
    embeddings = model.encode(texts).tolist()
    ids = [str(i) for i in range(len(texts))]
    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids
    )

def similarity_search(query: str, k: int = 3):
    embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=embedding,
        n_results=k
    )
    return results["documents"][0]
