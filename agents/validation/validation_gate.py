from agents.LLM.llm import ask_llm

class ValidationGate:
    """
    Validates AI outputs before sending to user.
    Ensures responses are safe, accurate, and helpful.
    Also refines responses to add context around raw code.
    """
    
    def __init__(self):
        self.criteria = [
            "helpful and relevant",
            "factually accurate",
            "safe and appropriate",
            "clear and well-structured",
            "complete answer to the question"
        ]
    
    def validate(self, query: str, response: str) -> tuple[bool, str]:
        """
        Validate if the response is ready for the user.
        
        Args:
            query: The original user query
            response: The AI's response
        
        Returns:
            (is_valid, feedback) tuple
        """
        prompt = f"""
You are a quality assurance validator. Check if this AI response is ready for the user.

Original question: {query}

AI response: {response}

Check if the response is:
- Helpful and relevant to the question
- Factually accurate (no hallucinations)
- Safe and appropriate content
- Clear and well-structured
- Complete answer
- Not just raw code (should have explanatory text around code blocks)

Return your answer in this exact format:
VALID: [true/false]
FEEDBACK: [your feedback if not valid, or "OK" if valid]
"""
        
        result = ask_llm(prompt)
        
        if "VALID: true" in result.lower():
            return True, "OK"
        else:
            return False, result
    
    def refine_response(self, query: str, response: str) -> str:
        """
        Refine a response to add context and explanation around code.
        """
        # Check if response contains code blocks
        has_code = "```" in response
        
        if not has_code:
            # No code in response, return as-is
            return response
        
        prompt = f"""
Refine this AI response to make it more user-friendly.

Original question: {query}

Original response: {response}

The response contains code. Add:
- A brief introduction explaining what the code does
- Any necessary context or explanation
- A conclusion or next steps

Keep the code exactly as-is, just add explanatory text around it.

IMPORTANT: Return ONLY the refined response. Do not include any meta-commentary about the refinement process or what you changed. Just output the final response directly.
"""
        return ask_llm(prompt)
    
    def improve_response(self, query: str, response: str, feedback: str) -> str:
        """
        Improve a response based on validation feedback.
        """
        prompt = f"""
Improve this AI response based on the validation feedback.

Original question: {query}

Original response: {response}

Validation feedback: {feedback}

Provide an improved response that addresses all the feedback.
"""
        return ask_llm(prompt)
