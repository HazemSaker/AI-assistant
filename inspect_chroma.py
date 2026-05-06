"""
Script to inspect ChromaDB contents
"""
from agents.RAG.chroma_retriever import ChromaRetriever

def main():
    retriever = ChromaRetriever()
    count = retriever.count()
    print(f"Total chunks in database: {count}")
    
    # Get all documents
    collection = retriever.collection
    results = collection.get()
    
    print(f"\nTotal documents retrieved: {len(results['documents'])}")
    print("\nFirst 10 chunks:")
    for i, doc in enumerate(results['documents'][:10]):
        print(f"\n--- Chunk {i+1} ---")
        print(doc[:200])
        print("...")
    
    # Search for "author" or "manhas"
    print("\n\nSearching for 'author'...")
    results = retriever.search("author", n_results=5)
    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(doc[:200])
        print("...")

if __name__ == "__main__":
    main()
