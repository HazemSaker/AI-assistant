import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path

class ChromaRetriever:
    """ChromaDB-based retriever for RAG"""
    
    def __init__(self, collection_name="documents", persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def add_documents(self, chunks: list, metadatas: list = None):
        """Add document chunks to ChromaDB"""
        if metadatas is None:
            metadatas = [{"chunk_id": i} for i in range(len(chunks))]
        
        embeddings = self.embedding_model.encode(chunks)
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> list:
        """Search for relevant chunks"""
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Return documents
        return results['documents'][0] if results['documents'] else []
    
    def count(self) -> int:
        """Get number of chunks in collection"""
        return self.collection.count()
