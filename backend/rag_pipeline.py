from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import os  # Import os module
import torch
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
import re

from dotenv import load_dotenv  # Import load_dotenv

# Optional: login to HuggingFace for gated models

# Load variables from .env
load_dotenv()

# Get token from environment
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Login to Hugging Face
from huggingface_hub import login  # Import login function
login(token=token)

# try:
#     from huggingface_hub import login
#     login(token=HUGGINGFACEHUB_API_TOKEN)
# except Exception as e:
#     print(f"Warning: Could not login to HuggingFace: {e}")

class RAGPipeline:
    """Lightweight RAG pipeline that extracts answers from context without LLM generation"""
    def __init__(self, model_size: str = "small"):
        print(f"Initializing SimpleRAG Pipeline (no model download required)...")
        self.model_name = "simple-extractive-rag"
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"[Source {i}]: {doc['text']}")
        return "\n".join(context_parts)
    
    def generate_answer(self, question: str, context: str) -> str:
        """Extract relevant sentences from context based on question keywords"""
        if not context.strip():
            return "No relevant documents found to answer this question."
        
        # Simple keyword matching
        question_words = set(word.lower() for word in re.findall(r'\w+', question))
        sentences = [s.strip() for s in context.split('.') if s.strip()]
        
        # Score sentences by keyword match
        scored_sentences = []
        for sentence in sentences:
            score = sum(1 for word in question_words if word in sentence.lower())
            if score > 0:
                scored_sentences.append((sentence, score))
        
        if scored_sentences:
            # Return top 2 most relevant sentences
            sorted_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)
            answer = ". ".join([s[0] for s in sorted_sentences[:2]]) + "."
            return answer
        else:
            # Return first sentence if no keyword match
            return sentences[0] + "." if sentences else "Unable to find relevant information."
    
    def query(self, question: str, retrieved_docs: List[Dict]) -> Dict:
        context = self.format_context(retrieved_docs)
        answer = self.generate_answer(question, context)
        
        return {
            "question": question,
            "answer": answer,
            "context": context,
            "sources": retrieved_docs
        }
