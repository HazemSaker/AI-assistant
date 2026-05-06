from rank_bm25 import BM25Okapi
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")

class HybridRetriever:
    def __init__(self, chunks, embeddings):
        self.chunks = chunks

        # FAISS
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings))

        # BM25
        tokenized = [chunk.split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query, k=5):
        # Dense search
        query_vec = model.encode([query])
        _, dense_idx = self.index.search(query_vec, k)

        dense_results = [self.chunks[i] for i in dense_idx[0]]

        # Sparse search
        tokenized_query = query.split()
        sparse_scores = self.bm25.get_scores(tokenized_query)

        sparse_idx = np.argsort(sparse_scores)[-k:]
        sparse_results = [self.chunks[i] for i in sparse_idx]

        # Merge while preserving order
        seen = set()
        results = []

        for r in dense_results + sparse_results:
            if r not in seen:
                seen.add(r)
                results.append(r)

        return results[:k]