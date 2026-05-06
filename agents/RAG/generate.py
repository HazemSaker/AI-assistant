from agents.LLM.llm import ask_llm

def generate_answer(query, context_chunks, history=None):
    context = "\n".join(context_chunks)

    prompt = f"""
You are a strict AI assistant.

Rules:
- Answer ONLY using the provided context
- If the answer is not in the context, say: "I don't know"
- Do NOT make up information

Context:
{context}

Question:
{query}

Answer:
"""

    return ask_llm(prompt, history)