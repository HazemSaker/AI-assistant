from agents.LLM.llm import ask_llm
import ast

def rewrite_query(query: str) -> str:
    prompt = f"""
Rewrite the following question to be clear and specific.

Question:
{query}

Rewritten:
"""
    return ask_llm(prompt).strip()


def generate_queries(query: str, n=3) -> list[str]:
    prompt = f"""
Generate {n} different versions of this question for document retrieval.

Return ONLY a Python list.
Example: ["query1", "query2", "query3"]

Question:
{query}
"""

    response = ask_llm(prompt)

    try:
        queries = ast.literal_eval(response)
        if isinstance(queries, list):
            return queries
    except:
        pass

    # fallback
    return [query]