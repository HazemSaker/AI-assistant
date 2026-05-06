import subprocess
import json
from agents.LLM.llm import ask_llm

class ToolExecutionAgent:
    """
    Agent that can execute basic tools and commands.
    Supports: file operations, basic shell commands, code execution
    """
    
    def __init__(self):
        self.available_tools = {
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_files": self._list_files,
            "run_command": self._run_command,
            "search_files": self._search_files,
            "write_code": self._write_code
        }
    
    def run(self, query: str, context: str = None) -> str:
        """
        Analyze query and execute appropriate tool.
        """
        prompt = f"""
You are a tool execution agent. Determine which tool to use based on the user's request.

Available tools:
- read_file: Read contents of a file (args: path - string file path)
- write_file: Write content to a file (args: path - string file path, content - string content to write)
- list_files: List files in a directory (args: path - string directory path, default ".")
- run_command: Execute a shell command (args: command - string command to execute, keep it simple)
- search_files: Search for text in files (args: path - string directory path, pattern - string regex pattern)
- write_code: Write Python code to a file (args: code - string Python code, filename - optional filename)

User request: {query}
Context: {context if context else "None"}

IMPORTANT: For code generation requests, use the "write_code" tool instead of run_command.
When generating code, write clean, well-formatted Python code with:
- Proper indentation (4 spaces per level)
- Docstrings on new lines and indented
- Function body indented correctly
- No one-liners for functions
- Follow PEP 8 style guidelines

Return ONLY the tool name and arguments in JSON format:
{{"tool": "tool_name", "args": {{"arg1": "value1", ...}}}}
"""
        
        response = ask_llm(prompt)
        
        try:
            # Clean up response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            tool_call = json.loads(response)
            tool_name = tool_call.get("tool")
            args = tool_call.get("args", {})
            
            # Map common argument name variations
            if "file" in args and "path" not in args:
                args["path"] = args.pop("file")
            
            if tool_name in self.available_tools:
                return self.available_tools[tool_name](**args)
            else:
                return f"Unknown tool: {tool_name}"
        except json.JSONDecodeError as e:
            return f"Could not parse tool call: {response}. Error: {str(e)}"
    
    def _read_file(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _write_file(self, path: str, content: str) -> str:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def _list_files(self, path: str = ".") -> str:
        try:
            import os
            files = os.listdir(path)
            return "\n".join(files)
        except Exception as e:
            return f"Error listing files: {str(e)}"
    
    def _run_command(self, command: str) -> str:
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
    
    def _search_files(self, path: str, pattern: str) -> str:
        try:
            import os
            import re
            matches = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if re.search(pattern, file, re.IGNORECASE):
                        matches.append(os.path.join(root, file))
            return "\n".join(matches) if matches else "No matches found"
        except Exception as e:
            return f"Error searching files: {str(e)}"
    
    def _write_code(self, code: str, filename: str = "temp_code.py") -> str:
        """Write Python code to a file and verify syntax with retry"""
        try:
            import os
            from pathlib import Path
            
            # Create temp directory if needed
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            # Retry loop for syntax validation
            max_attempts = 3
            for attempt in range(max_attempts):
                # Write code to file
                file_path = temp_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                # Verify syntax by compiling (not executing)
                try:
                    compile(code, filename, 'exec')
                    # Return just the code without validation messages
                    return f"```python\n{code}\n```"
                except SyntaxError as e:
                    print(f"[ToolAgent] Syntax error on attempt {attempt + 1}: {str(e)}")
                    if attempt < max_attempts - 1:
                        # Ask LLM to fix the code
                        fix_prompt = f"""
The following Python code has a syntax error: {str(e)}

Code:
{code}

Please fix the syntax error and return only the corrected code. Ensure proper formatting and indentation.
"""
                        code = ask_llm(fix_prompt)
                        # Clean up the response
                        code = code.strip()
                        if code.startswith("```"):
                            code = code.split("```")[1]
                            if code.startswith("python"):
                                code = code[6:]
                        code = code.strip()
                    else:
                        return f"Code has syntax error after {max_attempts} attempts: {str(e)}"
        except Exception as e:
            return f"Error verifying code: {str(e)}"
