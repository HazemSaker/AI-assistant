from sentence_transformers import SentenceTransformer
import os

model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")

def load_documents() -> str:
    documents_text = ""

    for f in os.listdir("data"):
        with open(os.path.join("data", f), encoding="utf-8") as t:
            documents_text += t.read() + "\n"

    return documents_text


def chunk_text(text: str, chunk_size=300, overlap=50) -> list:
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def create_embeddings(chunks):
    return model.encode(chunks)