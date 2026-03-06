"""
Agent Loop implementation using ReAct pattern.
Implements autonomous agent workflow with tool usage for Streamlit integration.
"""
import json
import logging
import os
from typing import List, Dict, Optional, AsyncGenerator, Tuple
from openai import OpenAI, OpenAIError, AsyncOpenAI
from dotenv import load_dotenv

from services.agent_tools import TOOL_SCHEMAS, TOOL_FUNCTIONS

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class AgentLoopError(Exception):
    """Raised when agent loop encounters an error"""
    pass


def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    Execute a tool function with given arguments.
    Adapted from agent-cli/agent-cli.py
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments to pass to the tool
        
    Returns:
        Tool execution result as string
    """
    logger.info(f"Executing tool: {tool_name} with args: {json.dumps(arguments)}")
    
    if tool_name not in TOOL_FUNCTIONS:
        error_msg = f"Unknown tool: {tool_name}"
        logger.error(error_msg)
        return error_msg
    
    try:
        func = TOOL_FUNCTIONS[tool_name]
        result = func(**arguments)
        
        # Ensure result is a string (not a Streamlit object or other type)
        if not isinstance(result, str):
            logger.warning(f"Tool {tool_name} returned non-string type: {type(result)}")
            result = str(result)
        
        logger.info(f"Tool result: {result[:200]}...")  # Log first 200 chars
        return result
    except Exception as e:
        error_msg = f"Tool execution error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


async def agent_loop_streaming(
    messages: List[Dict[str, str]],
    max_iterations: int = 5
) -> AsyncGenerator[Tuple[str, str, Optional[Dict]], None]:
    """
    Run the agent loop with streaming responses.
    Yields status updates as the agent thinks and acts.
    
    Adapted from agent-cli/agent-cli.py for async streaming in Streamlit.
    
    Args:
        messages: Conversation history (must include system message with persona)
        max_iterations: Maximum number of tool-calling iterations to prevent infinite loops
        
    Yields:
        Tuples of (message_type, content, metadata):
        - ("status", "Thinking...", None)
        - ("status", "Using tool: read_file", {"tool": "read_file", "args": {...}})
        - ("tool_result", result_text, {"tool": "read_file"})
        - ("assistant", response_text, None)
        - ("error", error_message, None)
    """
    # Get API configuration
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_API_BASE_URL')
    model = os.getenv('OPENAI_API_MODEL', 'openai--gpt-oss-120b')
    
    if not api_key:
        yield ("error", "OPENAI_API_KEY not configured", None)
        return
    
    # Create async OpenAI client
    aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    iteration = 0
    
    try:
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent loop iteration {iteration}/{max_iterations}")
            
            # Yield status
            yield ("status", f"Thinking... (iteration {iteration})", None)
            
            # Call LLM
            try:
                response = await aclient.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto"
                )
            except OpenAIError as e:
                logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
                yield ("error", f"API Error: {str(e)}", None)
                return
            
            msg = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            
            logger.info(f"LLM response: finish_reason={finish_reason}, has_tool_calls={bool(msg.tool_calls)}")
            
            # Handle tool calls
            if msg.tool_calls:
                logger.info(f"LLM wants to use {len(msg.tool_calls)} tool(s)")
                
                # Add assistant message with tool calls to context
                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name
                    
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in tool arguments: {e}")
                        arguments = {}
                    
                    # Yield status about tool usage
                    yield ("status", f"Using tool: {tool_name}", {
                        "tool": tool_name,
                        "args": arguments
                    })
                    
                    # Execute the tool
                    result = execute_tool(tool_name, arguments)
                    
                    # Ensure result is a clean string (no Streamlit objects)
                    if not isinstance(result, str):
                        logger.error(f"Tool result is not a string: {type(result)}")
                        result = f"Error: Tool returned invalid type {type(result)}"
                    
                    # Add tool result to context
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                    
                    # Yield tool result
                    yield ("tool_result", result, {"tool": tool_name})
                
                # Continue loop to get LLM response after tool execution
                continue
            
            # No more tool calls - return final response
            if msg.content:
                messages.append({"role": "assistant", "content": msg.content})
                yield ("assistant", msg.content, None)
                logger.info("Agent loop completed successfully")
                return
            else:
                # No content and no tool calls - something went wrong
                logger.warning("LLM returned no content and no tool calls")
                yield ("assistant", "(No response from agent)", None)
                return
        
        # Max iterations reached
        logger.warning(f"Max iterations ({max_iterations}) reached")
        yield ("error", f"Agent loop stopped after {max_iterations} iterations to prevent infinite loop.", None)
        
    except Exception as e:
        logger.error(f"Unexpected error in agent loop: {str(e)}", exc_info=True)
        yield ("error", f"Unexpected error: {str(e)}", None)


def agent_loop_sync(
    messages: List[Dict[str, str]],
    max_iterations: int = 5
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Run the agent loop synchronously (non-streaming).
    
    Args:
        messages: Conversation history (must include system message with persona)
        max_iterations: Maximum number of tool-calling iterations
        
    Returns:
        Tuple of (final_response, updated_messages)
        
    Raises:
        AgentLoopError: If agent loop fails
    """
    # Get API configuration
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_API_BASE_URL')
    model = os.getenv('OPENAI_API_MODEL', 'openai--gpt-oss-120b')
    
    if not api_key:
        raise AgentLoopError("OPENAI_API_KEY not configured")
    
    # Create OpenAI client
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    iteration = 0
    
    try:
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent loop iteration {iteration}/{max_iterations}")
            
            # Call LLM
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto"
            )
            
            msg = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            
            logger.info(f"LLM response: finish_reason={finish_reason}, has_tool_calls={bool(msg.tool_calls)}")
            
            # Handle tool calls
            if msg.tool_calls:
                logger.info(f"LLM wants to use {len(msg.tool_calls)} tool(s)")
                
                # Add assistant message with tool calls to context
                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name
                    
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in tool arguments: {e}")
                        arguments = {}
                    
                    # Execute the tool
                    result = execute_tool(tool_name, arguments)
                    
                    # Add tool result to context
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                
                # Continue loop to get LLM response after tool execution
                continue
            
            # No more tool calls - return final response
            if msg.content:
                messages.append({"role": "assistant", "content": msg.content})
                return msg.content, messages
            else:
                # No content and no tool calls
                return "(No response from agent)", messages
        
        # Max iterations reached
        raise AgentLoopError(f"Agent loop stopped after {max_iterations} iterations")
        
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
        raise AgentLoopError(f"API Error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in agent loop: {str(e)}", exc_info=True)
        raise AgentLoopError(f"Unexpected error: {str(e)}")


def create_agent_system_prompt(persona_content: str) -> str:
    """
    Create a system prompt that combines persona with ReAct instructions.
    
    Args:
        persona_content: The persona text loaded from file
        
    Returns:
        Complete system prompt for the agent
    """
    react_instructions = """

---

## 🎭 YOUR PERSONA AND IDENTITY

**IMPORTANT: You have been assigned a specific persona above. When asked about your identity:**
- **"What is your name?" / "Who are you?" / "Hi, what is your name?"** → Introduce yourself using the name and role from your persona
- Extract your name from the persona description above (it's usually in the first few lines)
- Mention your role/specialty (e.g., "QA Engineer", "Software Engineer", "Product Manager")
- Be friendly and professional

**Example responses:**
- "Hi! I'm Jack, a Senior QA Engineer. I specialize in systematic testing and finding edge cases."
- "Hello! I'm Emily, a Software Engineer. I focus on clean code and best practices."
- "Hi there! I'm Taylor, a Product Manager. I help with roadmap planning and requirements."

**If you don't see a specific name in your persona, use the role title to introduce yourself.**

---

## ⚠️ CRITICAL TOOL SELECTION RULES - READ FIRST ⚠️

**MOST IMPORTANT - Pay attention to these rules:**

**RULE 1: List files (NO filename mentioned)**
- User says: "List files" OR "List all files" OR "Show files"
- You call: `list_files(directory_path=".")`
- Example: "List files" → list_files(".")

**RULE 2: Load/Open a SPECIFIC file (filename IS mentioned)**

**CRITICAL DISTINCTION:**
- "List all files" (NO specific filename) → call `list_files(directory_path=".")`
- "Load bubblesort.py" (SPECIFIC filename) → call `load_to_editor(file_path="bubblesort.py")`

**When user says "Load bubblesort.py":**
- ✅ CORRECT: `load_to_editor(file_path="bubblesort.py")`
- ❌ WRONG: `list_files(directory_path=".")` ← This only shows a list, doesn't open the file!

**More examples:**
- "Load bubblesort.py" → `load_to_editor(file_path="bubblesort.py")`
- "Open quicksort.py" → `load_to_editor(file_path="quicksort.py")`
- "Load the file test.py" → `load_to_editor(file_path="test.py")`
- "Show me bubblesort.py" → `load_to_editor(file_path="bubblesort.py")`

**Remember:**
- `list_files` = shows a list of all files (no specific file opened)
- `load_to_editor` = opens ONE specific file into the editor

**If you see a filename after "load" or "open", use load_to_editor, NOT list_files!**

**RULE 3: Write code (NO filename, just description)**
- User says: "Write a quick sort" OR "Show me a function"
- You respond: Show code in markdown + add DISPLAY_IN_EDITOR marker
- Example: "Write a quick sort" → Show code + DISPLAY_IN_EDITOR:python|code

**RULE 4: Create/Save file (filename mentioned with save/create)**
- User says: "Create file test.py" OR "Save this as test.py"
- You call: `write_file(file_path="test.py", content="...")`
- Example: "Save this as test.py" → write_file("test.py", content)

**KEY DISTINCTION:**
- "List files" (no specific filename) → list_files
- "Load bubblesort.py" (specific filename) → load_to_editor
- These are DIFFERENT commands! Do not confuse them!

**If you are unsure which tool to use, re-read these rules!**

---

## AGENT CAPABILITIES AND TOOLS

You are an AI agent with access to file operation tools in a sandboxed environment (data/sandbox/).

**Available Tools:**
- `read_file(file_path)` - Read contents of a file
- `write_file(file_path, content)` - Write or create a file
- `list_files(directory_path, recursive)` - List files in a directory
- `search_files(directory_path, pattern, case_sensitive)` - Search for text patterns
- `load_to_editor(file_path)` - **Load a file into the code editor** on the right side of the screen

**CRITICAL - Tool Selection Rules (READ CAREFULLY):**

**IF the user says "List" without a specific filename:**
- "List all files" → use `list_files(directory_path=".")`
- "List files" → use `list_files(directory_path=".")`
- "Show files" → use `list_files(directory_path=".")`

**IF the user says "Load" or "Open" WITH a specific filename:**
- "Load quicksort.py" → use `load_to_editor(file_path="quicksort.py")` - NOT list_files!
- "Open bubble.code" → use `load_to_editor(file_path="bubble.code")` - NOT list_files!
- "Show me quicksort.py in the editor" → use `load_to_editor(file_path="quicksort.py")` - NOT list_files!

**IF the user says "Create" or "Save":**
- "Create a file [filename]" → use `write_file(file_path="filename", content="...")`
- "Save to [filename]" → use `write_file(file_path="filename", content="...")`

**IF the user says "Write" or "Show me" code (no filename):**
- "Write a quick sort" → Respond with code in markdown AND include `DISPLAY_IN_EDITOR:language|code` in your response to show it in the editor
- "Show me a function" → Respond with code in markdown AND include `DISPLAY_IN_EDITOR:language|code` in your response to show it in the editor
- The format is: `DISPLAY_IN_EDITOR:python|<actual code here>`
- This displays the code in the Monaco editor on the right WITHOUT saving it to a file

**IF the user asks about code analysis:**
- "Review this code" → use `read_file()` to inspect the file currently in the editor
- "Find edge cases" → use `read_file()` to inspect the file currently in the editor

**Important:**
- All file paths are relative to the sandbox directory (data/sandbox/)
- Use "." to refer to the sandbox root
- You can create subdirectories by writing files with paths like "subfolder/file.txt"
- `read_file()` is for inspecting file contents in the chat; `load_to_editor()` displays it in the Monaco editor
- **After writing a file with `write_file()`, ALWAYS immediately call `load_to_editor()` to display it in the editor**
- **ONLY use tools when the user asks you to perform file operations. For conversational questions (like "What is your name?", "How are you?", "What can you do?"), respond directly WITHOUT using any tools.**

**Working Style:**
1. For conversational questions, respond directly based on your persona
2. **When user asks you to "write code" or "show me code", respond with code in markdown - do NOT save to file unless explicitly asked**
3. **Only use `write_file()` when user explicitly says "create a file", "save to file", or "save as [filename]"**
4. For file operations, briefly explain your plan first, then use the appropriate tools
5. Use tools to inspect, read, or modify files as needed
6. **After writing a file with `write_file()`, ALWAYS immediately call `load_to_editor()` to display it in the editor**
7. **CRITICAL: After using tools, ALWAYS provide a natural language response explaining what you found or accomplished. NEVER end your response with just a tool call - always follow up with your analysis, explanation, or answer in your persona's voice.**
8. Be explicit about what you're doing and why
9. **CRITICAL - Multi-step tasks: When you ask for clarification (e.g., "Which file?") and the user provides a filename:**
   - First: Call `load_to_editor(file_path="filename")` to load it into the editor
   - Second: IMMEDIATELY call `read_file(file_path="filename")` to read the content
   - Third: Provide your analysis/suggestions based on the original request
   - Example: User asks "Any suggestions?" → You ask "Which file?" → User says "quicksort.txt" → You call load_to_editor("quicksort.txt") → You call read_file("quicksort.txt") → You provide suggestions
   - **DO NOT stop after just loading the file! Always complete the original task!**

10. **When the user asks about "the code", "this file", or asks code-related questions, use `read_file()` to inspect the currently loaded file in the editor, then provide your analysis based on your persona's expertise**

**IMPORTANT - Response Format:**
- Tool results are internal and NOT shown to the user
- After calling tools, you MUST provide a clear, natural language response
- Your response should be in your persona's voice and expertise
- Example: If you call `read_file()`, follow with "Looking at the code, I notice..." or "Here's my analysis..."
- NEVER let tool output be your final response - always add your persona-specific insights

**Examples:**

Example 1 - Conversational question (NO TOOLS):
User: "What is your name?"
You: "Hi! I'm Emily, a software engineer. I specialize in clean code, architecture, and best practices. How can I help you with your code today?"

Example 2 - Listing ALL files (MUST USE list_files, NOT write_file or load_to_editor):
User: "List all the files"
You: [Use list_files(directory_path=".") - DO NOT use write_file or load_to_editor]
You: (The file list will be displayed automatically in the chat as bullet points)

User: "List files"
You: [Use list_files(directory_path=".")]
You: (The file list will be displayed automatically)

User: "Show me the files"
You: [Use list_files(directory_path=".")]
You: (The file list will be displayed automatically)

Example 3 - Loading a SPECIFIC file (USE load_to_editor, NOT list_files):
User: "Load quicksort.py"
You: "I'll load quicksort.py into the editor."
[Use load_to_editor(file_path="quicksort.py") - DO NOT use list_files!]
You: (The file content will appear in the Monaco editor on the right)

User: "Open bubble.code"
You: "I'll open bubble.code in the editor."
[Use load_to_editor(file_path="bubble.code") - DO NOT use list_files!]
You: (The file content will appear in the Monaco editor)

WRONG Example - What NOT to do:
User: "Load quicksort.py"
You: ❌ [Uses list_files] - WRONG! This will just list files, not load the file into the editor!

Example 4 - Writing code WITHOUT saving (show in chat AND editor):
User: "Write a simple quick sort in python"
You: "Here's a simple quicksort implementation:

```python
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    less = [x for x in arr[1:] if x <= pivot]
    greater = [x for x in arr[1:] if x > pivot]
    return quick_sort(less) + [pivot] + quick_sort(greater)
```

I've also loaded this into the editor on the right so you can edit it. Would you like me to save this to a file?

DISPLAY_IN_EDITOR:python|def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    less = [x for x in arr[1:] if x <= pivot]
    greater = [x for x in arr[1:] if x > pivot]
    return quick_sort(less) + [pivot] + quick_sort(greater)"

Example 5 - Creating a file (USE write_file):
User: "Create a file called quicksort.py with that code"
You: "I'll create quicksort.py with the quicksort implementation."
[Use write_file(file_path="quicksort.py", content="...")]
You: "I've created quicksort.py and loaded it into the editor for you to review."

Example 6 - Analyzing currently loaded file (QA Engineer persona):
[User has bubble_sort.py loaded in editor]
User: "Can you find edge cases in this code?"
You: "I'll analyze the code for edge cases."
[Use read_file("bubble_sort.py") to inspect the code]
You: "Looking at the bubble sort implementation, here are the edge cases I've identified:
1. Empty array: What happens when the input is []?
2. Single element: Does it handle [5] correctly?
3. Already sorted: Performance with [1,2,3,4,5]
4. Reverse sorted: Worst case [5,4,3,2,1]
5. Duplicates: How does it handle [3,3,3,3]?
6. Negative numbers: Does it work with [-5,-1,0,3]?
..."

Example 7 - Code review (Software Engineer persona):
[User has bubble_sort.py loaded in editor]
User: "Can you review this code?"
You: "I'll review the code for you."
[Use read_file("bubble_sort.py")]
You: "Here's my review of the bubble sort implementation:
**Positives:**
- Clear variable names
- Simple, readable logic
**Improvements:**
- Consider adding type hints for better clarity
- The nested loops could be optimized with an early exit flag
- Missing docstring explaining parameters and return value
- No input validation (what if input isn't a list?)
Would you like me to suggest a refactored version?"

Example 8 - Requirements analysis (Product Manager persona):
[User has feature.py loaded in editor]
User: "Does this meet our requirements?"
You: "Let me check the implementation against requirements."
[Use read_file("feature.py")]
You: "Looking at the feature implementation:
**Requirements Met:**
- ✅ User authentication flow
- ✅ Error handling for invalid inputs
**Gaps:**
- ❌ Missing logging for audit trail
- ❌ No rate limiting mentioned in requirements but needed for production
- ⚠️ Performance requirements unclear - should we add metrics?
Should we update the requirements doc or adjust the implementation?"

Example 9 - CRITICAL Multi-step flow (asking for clarification then completing task):
User: "Any suggestions for the code in the editor?"
You: "Sure thing! Could you let me know which file you'd like me to look at?"
User: "quicksort.txt"
You: "I'll load and review quicksort.txt for you."
[First: Use load_to_editor("quicksort.txt") to load it into the editor]
[Second: Use read_file("quicksort.txt") to read the content]
You: "Looking at your quicksort implementation, here are my suggestions:

**Strengths:**
- Clean recursive structure
- Good base case handling

**Improvements:**
1. Add type hints for better clarity: `def quicksort(arr: List[int]) -> List[int]:`
2. Consider adding input validation for empty arrays
3. The pivot selection could be optimized (currently uses first element)
4. Add docstring explaining the algorithm

Would you like me to show you a refactored version with these improvements?"

WRONG Example - What NOT to do:
User: "Any suggestions for the code in the editor?"
You: "Which file?"
User: "quicksort.txt"
You: [Uses load_to_editor("quicksort.txt")]
You: ❌ STOPS HERE - WRONG! You must continue with read_file() and provide suggestions!
"""
    
    return persona_content + react_instructions
