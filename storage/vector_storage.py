import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List
from core.config import Config
from core.logger import logger
import os
from tqdm import tqdm
import shutil


class VectorStorage:
    """ChromaDB vector storage for RAG."""   
    
    def __init__(self, collection_name: str = "documents"):
        self.data_dir = Path(Config.DATA_DIR)
        self.processed_dir = Path(Config.PROCESSED_DIR)
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlab = Config.CHUNK_OVERLAP
        self.topk = Config.TOP_K_RESULTS
        
        # Initialize embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize Chroma Data Base
        self.client = chromadb.PersistentClient(path=Config.CHROMA_DIR)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.ingest_rag()
    
    def ingest_rag(self):
        """Add documents to vector store."""

        self.processed_dir.mkdir(exist_ok=True)
        
        # Get list of files to process (recursive, exclude processed folder)
        files_to_process = []
        for f in self.data_dir.rglob("*"):
            if f.is_file() and f.suffix in ['.txt', '.md', '.json', '.pdf']:
                files_to_process.append(f)
        
        if not files_to_process:
            logger.info("No documents found in data/ directory. Add some files first.")
            logger.info("Current data directory contents:")
            for item in self.data_dir.iterdir():
                logger.info(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")
            return
        
        logger.info(f"Found {len(files_to_process)} files to ingest:")
        for f in files_to_process:
            logger.info(f"  - {f}")
        
        # Load documents with progress bar
        documents_text = ""
        for file_path in tqdm(files_to_process, desc="Loading files"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents_text += f.read() + "\n"
            except Exception as e:
                logger.info(f"Error reading {file_path}: {e}")
        
        if not documents_text:
            logger.info("No text content found in files.")
            return
        
        logger.info(f"Loaded {len(documents_text)} characters of text")
        
        logger.info("Chunking text...")
        chunks = self.chunk_text(documents_text, chunk_size=self.chunk_size, overlap=self.chunk_overlab)
        logger.info(f"Created {len(chunks)} chunks")
        
        logger.info(f"Adding {len(chunks)} chunks to ChromaDB...")
        self.add_documents(chunks)
        logger.info(f"Total chunks in database: {self.count()}")
        
        # Move processed files
        logger.info("Moving processed files...")
        for file_path in tqdm(files_to_process, desc="Moving files"):
            try:
                dest = self.processed_dir / file_path.name
                shutil.move(str(file_path), str(dest))
            except Exception as e:
                logger.info(f"Error moving {file_path}: {e}")
        
        logger.info(f"Moved {len(files_to_process)} files to {self.processed_dir}")
        logger.info("RAG ingestion complete! Data stored in chroma_db/ directory")

    def search(self, query: str) -> List[str]:
        """Search for relevant documents."""
        # Generate query embedding
        query_embedding = self.embedder.encode([query]).tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=self.topk
        )
        
        # Return document texts
        documents = results.get("documents", [[]])
        return documents[0] if documents else []
    
    def count(self) -> int:
        """Get total number of documents."""
        return self.collection.count()
    
    def clear(self):
        """Clear all documents."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Vector storage cleared")


    def chunk_text(self, text: str, chunk_size=300, overlap=50) -> list:
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks


    def create_embeddings(self, chunks):
        return self.model.encode(chunks)
    
    def add_documents(self, chunks: list, metadatas: list = None):
        """Add document chunks to ChromaDB"""
        if metadatas is None:
            metadatas = [{"chunk_id": i} for i in range(len(chunks))]
        
        embeddings = self.embedder.encode(chunks)
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )
    