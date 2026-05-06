import re
from agents.LLM.llm import ask_llm

class DebuggingAgent:
    """
    Agent that helps debug code and technical issues.
    Analyzes errors, suggests fixes, and explains problems.
    """
    
    def __init__(self):
        pass
    
    def run(self, query: str, code: str = None, error: str = None) -> str:
        """
        Analyze debugging request and provide solution.
        
        Args:
            query: The user's debugging question
            code: Optional code snippet to analyze
            error: Optional error message
        
        Returns:
            Debugging analysis and solution
        """
        prompt = f"""
You are a debugging assistant. Help the user debug their code or technical issue.

User's question: {query}

Code to analyze:
{code if code else "No code provided"}

Error message:
{error if error else "No error provided"}

Provide:
1. Root cause analysis
2. Step-by-step solution
3. Code fix if applicable
4. Prevention tips

Be clear and concise.
"""
        
        return ask_llm(prompt)
    
    def analyze_error(self, error_message: str) -> str:
        """
        Analyze an error message and explain what went wrong.
        """
        prompt = f"""
Analyze this error message and explain:
1. What the error means
2. Common causes
3. How to fix it

Error: {error_message}
"""
        return ask_llm(prompt)
    
    def review_code(self, code: str, language: str = "python") -> str:
        """
        Review code for potential bugs and improvements.
        """
        prompt = f"""
Review this {language} code for:
1. Bugs
2. Logical errors
3. Performance issues
4. Best practices violations

Code:
{code}

Provide specific line-by-line feedback.
"""
        return ask_llm(prompt)
