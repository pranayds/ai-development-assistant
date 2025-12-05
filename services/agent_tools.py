"""
Built-in file operation tools for the agent.
Adapted from cs5740-project-agents/agent-cli/tools.py
All operations are sandboxed to data/sandbox/ directory.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Union


class SecurityError(Exception):
    """Raised when a path validation fails"""
    pass


def get_sandbox_root() -> Path:
    """
    Get the absolute path to the sandbox directory.
    
    Returns:
        Path object pointing to data/sandbox/
    """
    # Get the project root (where this file's parent's parent is)
    project_root = Path(__file__).parent.parent
    sandbox = project_root / "data" / "sandbox"
    
    # Create sandbox if it doesn't exist
    sandbox.mkdir(parents=True, exist_ok=True)
    
    return sandbox.resolve()


def validate_path(path_str: str) -> Path:
    """
    Validate that a path is within the sandbox directory.
    
    Args:
        path_str: Path string to validate (relative to sandbox)
        
    Returns:
        Resolved Path object
        
    Raises:
        SecurityError: If path is outside sandbox directory
    """
    try:
        sandbox_root = get_sandbox_root()
        
        # Resolve the path relative to sandbox
        if Path(path_str).is_absolute():
            raise SecurityError(f"Absolute paths not allowed: {path_str}")
        
        resolved = (sandbox_root / path_str).resolve()
        
        # Check if resolved path starts with sandbox_root
        if not str(resolved).startswith(str(sandbox_root)):
            raise SecurityError(f"Access denied - path outside sandbox: {path_str}")
        
        return resolved
    except Exception as e:
        if isinstance(e, SecurityError):
            raise
        raise SecurityError(f"Invalid path: {path_str} - {str(e)}")


def read_file(file_path: str) -> str:
    """
    Read and return the contents of a file in the sandbox.
    
    Args:
        file_path: Path to the file to read (relative to sandbox)
        
    Returns:
        File contents as a string
    """
    try:
        safe_path = validate_path(file_path)
        
        if not safe_path.exists():
            return f"Error: File not found: {file_path}"
        
        if not safe_path.is_file():
            return f"Error: Path is not a file: {file_path}"
        
        # Read as text - may fail on binary files
        try:
            content = safe_path.read_text(encoding='utf-8')
            return content
        except UnicodeDecodeError:
            return f"Error: Cannot read binary file as text: {file_path}"
            
    except SecurityError as e:
        return f"Security Error: {str(e)}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file in the sandbox, creating it if it doesn't exist.
    Automatically loads the file into the editor after writing.
    
    Args:
        file_path: Path to the file to write (relative to sandbox)
        content: Content to write to the file
        
    Returns:
        Success message with auto-load marker or error description
    """
    try:
        safe_path = validate_path(file_path)
        
        # Create parent directories if they don't exist
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the content
        safe_path.write_text(content, encoding='utf-8')
        
        # Detect language from extension for auto-load
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'plaintext',
            '.code': 'plaintext'  # Generic code files
        }
        language = ext_to_lang.get(safe_path.suffix.lower(), 'plaintext')
        
        # Return special marker to trigger auto-load to editor WITH full content
        # This ensures the Monaco editor shows the complete file immediately
        line_count = len(content.splitlines())
        result = f"LOAD_TO_EDITOR:{file_path}|{language}|{line_count} lines\n\n"
        result += f"Successfully wrote {file_path} to sandbox.\n\n"
        result += f"Contents of {file_path}:\n```{language}\n{content}\n```\n\n"
        result += f"The file has been written and loaded into the editor."
        return result
        
    except SecurityError as e:
        return f"Security Error: {str(e)}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_files(directory_path: str = ".", recursive: bool = False) -> str:
    """
    List files in a directory within the sandbox.
    
    Args:
        directory_path: Path to the directory to list (default: sandbox root, use "." for root)
        recursive: Whether to list files recursively
        
    Returns:
        Formatted list of files or error description
    """
    try:
        safe_path = validate_path(directory_path)
        
        if not safe_path.exists():
            return f"Error: Directory not found: {directory_path}"
        
        if not safe_path.is_dir():
            return f"Error: Path is not a directory: {directory_path}"
        
        files = []
        
        if recursive:
            # Recursive listing
            for item in safe_path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(safe_path)
                    files.append(str(rel_path))
        else:
            # Top-level listing only
            for item in safe_path.iterdir():
                if item.is_file():
                    files.append(item.name)
                elif item.is_dir():
                    files.append(f"{item.name}/")
        
        files.sort()
        
        if not files:
            return f"No files found in {directory_path}"
        
        result = f"Files in {directory_path}:\n"
        result += "\n".join(f"  - {f}" for f in files)
        return result
        
    except SecurityError as e:
        return f"Security Error: {str(e)}"
    except Exception as e:
        return f"Error listing files: {str(e)}"


def load_to_editor(file_path: str) -> str:
    """
    Load a file from the sandbox into the code editor.
    This is a special tool that updates the editor state.
    
    Args:
        file_path: Path to the file to load (relative to sandbox)
        
    Returns:
        Success message with file info
    """
    try:
        abs_path = validate_path(file_path)
        
        if not abs_path.exists():
            return f"Error: File '{file_path}' does not exist in the sandbox"
        
        if not abs_path.is_file():
            return f"Error: '{file_path}' is not a file"
        
        # Read the file content
        try:
            content = abs_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return f"Error: File '{file_path}' is not a text file (binary content detected)"
        
        # Detect language from extension
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'plaintext',
            '.code': 'plaintext'  # Generic code files
        }
        language = ext_to_lang.get(abs_path.suffix.lower(), 'plaintext')
        
        # CRITICAL FIX: Return both the marker AND the full file contents
        # The marker triggers UI updates, and the content allows LLM to analyze the code
        line_count = len(content.splitlines())
        result = f"LOAD_TO_EDITOR:{file_path}|{language}|{line_count} lines\n\n"
        result += f"Contents of {file_path}:\n```{language}\n{content}\n```\n\n"
        result += f"The file has been loaded into the editor. You can now analyze this code."
        return result
        
    except SecurityError as e:
        return f"Security error: {str(e)}"
    except Exception as e:
        return f"Error loading file to editor: {str(e)}"


def search_files(directory_path: str, pattern: str, case_sensitive: bool = False) -> str:
    """
    Search for a text pattern in files within a directory in the sandbox.
    
    Args:
        directory_path: Path to the directory to search in (relative to sandbox)
        pattern: Text pattern to search for (plain text or regex)
        case_sensitive: Whether the search should be case-sensitive
        
    Returns:
        Formatted search results or error description
    """
    try:
        safe_path = validate_path(directory_path)
        
        if not safe_path.exists():
            return f"Error: Directory not found: {directory_path}"
        
        if not safe_path.is_dir():
            return f"Error: Path is not a directory: {directory_path}"
        
        # Compile regex pattern
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
        except re.error as e:
            return f"Error: Invalid regex pattern: {str(e)}"
        
        matches = []
        
        # Search all files recursively
        for file_path in safe_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    if regex.search(line):
                        rel_path = file_path.relative_to(safe_path)
                        matches.append({
                            'file': str(rel_path),
                            'line': line_num,
                            'content': line.strip()
                        })
            except (UnicodeDecodeError, PermissionError):
                # Skip binary files or files we can't read
                continue
        
        if not matches:
            return f"No matches found for pattern '{pattern}' in {directory_path}"
        
        # Format results
        result = f"Found {len(matches)} match(es) for '{pattern}':\n\n"
        
        # Group by file
        current_file = None
        for match in matches:
            if match['file'] != current_file:
                current_file = match['file']
                result += f"\n{current_file}:\n"
            result += f"  Line {match['line']}: {match['content']}\n"
        
        return result
        
    except SecurityError as e:
        return f"Security Error: {str(e)}"
    except Exception as e:
        return f"Error searching files: {str(e)}"


# Tool schemas for OpenAI function calling
# Adapted from agent-cli/tools.py for use with Ducky
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file in the sandbox. All paths are relative to data/sandbox/.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read, relative to sandbox directory (e.g., 'test.py' or 'subfolder/file.txt')"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file in the sandbox, creating it if it doesn't exist. All paths are relative to data/sandbox/.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write, relative to sandbox directory"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in the sandbox directory. Use this ONLY when the user asks 'list files', 'show files', 'what files are there' WITHOUT mentioning a specific filename. DO NOT use this for 'Load [filename]' or 'Open [filename]' - use load_to_editor instead! This tool ONLY shows filenames, it does NOT open files. Use '.' for sandbox root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory to list (default: '.' for sandbox root)",
                        "default": "."
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to list files recursively",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search for a text pattern in files within a directory in the sandbox. Supports regex patterns. All paths are relative to data/sandbox/.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory to search in (relative to sandbox)"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Text pattern to search for (plain text or regex)"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether the search should be case-sensitive",
                        "default": False
                    }
                },
                "required": ["directory_path", "pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_to_editor",
            "description": "**USE THIS TO OPEN FILES**: Load a SPECIFIC file into the Monaco code editor. Call this when the user says 'Load bubblesort.py', 'Open quicksort.py', 'Show me test.py', or any request to open/load a specific filename. This tool reads the file and displays it in the editor on the right. DO NOT use list_files for this! Example: User says 'Load bubblesort.py' → call load_to_editor with file_path='bubblesort.py'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the SPECIFIC file to load into the editor (e.g., 'quicksort.py', 'bubblesort.py'). This must be a filename, not a directory."
                    }
                },
                "required": ["file_path"]
            }
        }
    }
]


# Tool dispatch dictionary for safe execution
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "search_files": search_files,
    "load_to_editor": load_to_editor
}
