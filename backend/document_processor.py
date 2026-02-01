import os
from typing import List
import PyPDF2
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, documents_folder: str = "documents"):
        self.documents_folder = documents_folder
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def load_pdfs(self) -> List[Document]:
        """Load PDF documents"""
        documents = []
        
        for file_name in os.listdir(self.documents_folder):
            if file_name.endswith('.pdf'):
                file_path = os.path.join(self.documents_folder, file_name)
                
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                        
                        doc = Document(
                            page_content=text,
                            metadata={"source": file_name}
                        )
                        documents.append(doc)
                        print(f"Loaded PDF: {file_name}")
                        
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
        
        return documents
    
    def load_text_files(self) -> List[Document]:
        """Load text files"""
        documents = []
        
        for file_name in os.listdir(self.documents_folder):
            if file_name.endswith('.txt'):
                file_path = os.path.join(self.documents_folder, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                        
                        doc = Document(
                            page_content=text,
                            metadata={"source": file_name}
                        )
                        documents.append(doc)
                        print(f"Loaded TXT: {file_name}")
                        
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
        
        return documents
    
    def load_all_documents(self) -> List[Document]:
        """Load all supported documents"""
        documents = []
        documents.extend(self.load_pdfs())
        documents.extend(self.load_text_files())
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        if not documents:
            return []
        
        chunks = self.text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks

    # Backwards-compatible wrapper
    def load_documents(self) -> List[Document]:
        """Compatibility wrapper for older API: load_documents -> load_all_documents"""
        return self.load_all_documents()