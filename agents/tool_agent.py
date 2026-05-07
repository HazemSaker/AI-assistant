import subprocess
import json
from core.base import BaseAgent, AgentRequest, AgentResponse
from core.llm import OllamaLLM
from core.logger import logger
from core.config import Config


class ToolAgent(BaseAgent):
    """Tool execution agent for code generation and file operations."""
    
    def __init__(self):
        self.llm = OllamaLLM()
        self.max_retries = Config.MAX_RETRIES
    
    def handle(self, request: AgentRequest) -> AgentResponse:
        """Handle tool execution request."""
        query = request.user_input
        history = request.memory.get("chat_history", [])

        # Determine which tool to use
        tool_call = self.select_tool(query, history)
        
        if not tool_call:
            return AgentResponse(
                status="error",
                message="Could not determine appropriate tool."
            )
        
        # Execute the tool
        result = self.execute_tool(tool_call)
        
        return AgentResponse(
            status="success",
            data={"tool": tool_call["tool"], "result": result},
            message=result
        )
    
    def select_tool(self, query: str, history: list = None) -> dict:
        """Use LLM to select appropriate tool."""
        prompt = f"""
Select the appropriate tool for this request.

Available tools:
- write_code: Generate Python code (args: code)
- read_file: Read file contents (args: path)
- write_file: Write to file (args: path, content)
- run_command: Execute shell command (args: command)
- list_files: List directory (args: path)

Request: {query}

Return JSON: {{"tool": "tool_name", "args": {{"arg": "value"}}}}
"""

        response = self.llm.generate(prompt, history=history)
        
        try:
            # Clean response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse tool selection: {response}")
            return None
    
    def execute_tool(self, tool_call: dict) -> str:
        """Execute the selected tool."""
        tool = tool_call.get("tool")
        args = tool_call.get("args", {})
        
        if tool == "write_code":
            return self.write_code(args.get("code", ""))
        elif tool == "read_file":
            return self.read_file(args.get("path", ""))
        elif tool == "write_file":
            return self.write_file(args.get("path", ""), args.get("content", ""))
        elif tool == "run_command":
            return self.run_command(args.get("command", ""))
        elif tool == "list_files":
            return self.list_files(args.get("path", "."))
        else:
            return f"Unknown tool: {tool}"
    
    def write_code(self, code: str) -> str:
        """Generate and validate Python code with retry loop."""
        for attempt in range(self.max_retries):
            try:
                # Validate syntax
                compile(code, "<string>", "exec")
                return f"```python\n{code}\n```"
            except SyntaxError as e:
                if attempt < self.max_retries - 1:
                    # Ask LLM to fix
                    fix_prompt = f"Fix this syntax error: {str(e)}\n\nCode:\n{code}"
                    code = self.llm.generate(fix_prompt, history=[])
                    # Clean response
                    code = code.strip()
                    if code.startswith("```"):
                        code = code.split("```")[1]
                        if code.startswith("python"):
                            code = code[6:]
                    code = code.strip()
                else:
                    return f"Code has syntax error after {self.max_retries} attempts: {str(e)}"
        
        return code
    
    def read_file(self, path: str) -> str:
        """Read file contents."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write_file(self, path: str, content: str) -> str:
        """Write content to file."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def run_command(self, command: str) -> str:
        """Execute shell command."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return output if output else "Command executed with no output"
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error running command: {str(e)}"
    
    def list_files(self, path: str = ".") -> str:
        """List files in directory."""
        try:
            import os
            files = os.listdir(path)
            return "\n".join(files)
        except Exception as e:
            return f"Error listing files: {str(e)}"
