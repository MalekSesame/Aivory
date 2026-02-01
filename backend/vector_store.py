import chromadb
from chromadb.config import Settings
from typing import List, Optional
import os
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorStoreManager:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_collection(self, collection_name: str = "documents"):
        """Get or create a collection"""
        try:
            collection = self.client.get_collection(name=collection_name)
            print(f"Loaded existing collection: {collection_name}")
        except:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Created new collection: {collection_name}")
        
        return collection
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    def add_documents(self, documents: List[dict], collection_name: str = "documents"):
        """Add documents to the vector store"""
        collection = self.get_collection(collection_name)
        
        # Extract texts and metadata
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Add to collection
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        print(f"Added {len(documents)} documents to collection")
    
    def similarity_search(self, query: str, k: int = 5, collection_name: str = "documents") -> List[dict]:
        """Search for similar documents"""
        collection = self.get_collection(collection_name)
        
        # Create query embedding
        query_embedding = self.create_embeddings([query])[0]
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return formatted_results