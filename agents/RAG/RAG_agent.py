from agents.RAG.query import rewrite_query, generate_queries
from agents.RAG.generate import generate_answer
from agents.RAG.chroma_retriever import ChromaRetriever

class RAGAgent:
    def __init__(self, retriever=None):
        if retriever is None:
            # Auto-initialize ChromaDB if no retriever provided
            retriever = ChromaRetriever()
        self.retriever = retriever

    def run(self, query: str, history=None) -> str:
        print(f"[RAG] Running with query: {query}")
        
        # Check if database has any documents
        doc_count = self.retriever.count()
        print(f"[RAG] Database has {doc_count} chunks")
        
        if doc_count == 0:
            return "No documents in knowledge base. Please add documents to the data/ directory and run ingest_rag.py"
        
        # Skip query rewriting - use original query directly
        # rewritten = rewrite_query(query)
        # print(f"[RAG] Rewritten query: {rewritten}")
        
        # Skip query generation - use original query
        # queries = generate_queries(rewritten)
        queries = [query]
        print(f"[RAG] Using original query: {query}")

        all_results = []
        for q in queries:
            results = self.retriever.search(q)
            print(f"[RAG] Query '{q}' returned {len(results)} results")
            all_results.extend(results)

        # Clean + preserve order
        seen = set()
        context = []

        for r in all_results:
            if r not in seen:
                seen.add(r)
                context.append(r)
            if len(context) >= 3:
                break

        print(f"[RAG] Context chunks: {len(context)}")
        for i, chunk in enumerate(context):
            print(f"[RAG] Chunk {i+1}: {chunk[:100]}...")
        
        return generate_answer(query, context, history)