"""
Script to ingest documents into the RAG system using ChromaDB.
Run this after adding new documents to the data/ directory.
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm
from agents.RAG.chroma_retriever import ChromaRetriever

def chunk_text(text: str, chunk_size=300, overlap=50) -> list:
    """Split text into chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def main():
    data_dir = Path("data")
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    # Get list of files to process (recursive, exclude processed folder)
    files_to_process = []
    for f in data_dir.rglob("*"):
        if f.is_file() and f.suffix in ['.txt', '.md', '.json', '.pdf']:
            # Exclude files in processed folder
            if processed_dir not in f.parents:
                files_to_process.append(f)
    
    if not files_to_process:
        print("No documents found in data/ directory. Add some files first.")
        print("Current data directory contents:")
        for item in data_dir.iterdir():
            print(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")
        return
    
    print(f"Found {len(files_to_process)} files to ingest:")
    for f in files_to_process:
        print(f"  - {f}")
    
    # Load documents with progress bar
    documents_text = ""
    for file_path in tqdm(files_to_process, desc="Loading files"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                documents_text += f.read() + "\n"
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    if not documents_text:
        print("No text content found in files.")
        return
    
    print(f"Loaded {len(documents_text)} characters of text")
    
    print("Chunking text...")
    chunks = chunk_text(documents_text, chunk_size=300, overlap=50)
    print(f"Created {len(chunks)} chunks")
    
    print("Initializing ChromaDB...")
    retriever = ChromaRetriever()
    
    print(f"Adding {len(chunks)} chunks to ChromaDB...")
    retriever.add_documents(chunks)
    print(f"Total chunks in database: {retriever.count()}")
    
    # Move processed files
    print("Moving processed files...")
    for file_path in tqdm(files_to_process, desc="Moving files"):
        try:
            dest = processed_dir / file_path.name
            shutil.move(str(file_path), str(dest))
        except Exception as e:
            print(f"Error moving {file_path}: {e}")
    
    print(f"Moved {len(files_to_process)} files to {processed_dir}")
    print("RAG ingestion complete! Data stored in chroma_db/ directory")

if __name__ == "__main__":
    main()
