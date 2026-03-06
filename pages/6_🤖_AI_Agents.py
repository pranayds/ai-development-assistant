"""
AI Agents - Chat interface with ReAct-style agent loop
Autonomous agent system with tool integration and persona-based interactions
"""

import asyncio
import streamlit as st
from datetime import datetime

# Import services - agent system integration
from services.agent_loop import agent_loop_streaming, create_agent_system_prompt
from services.personas import get_available_personas, load_persona, get_persona_info
from ui.components.code_editor import render_code_editor
from ui.components.sidebar import render_sidebar

st.set_page_config(page_title="AI Agents", layout="wide")

# Render sidebar with logo and reload button
render_sidebar()

# Custom CSS for proper side padding matching AI Code Assistant page
st.markdown("""
<style>
/* Increase left/right padding to match AI Code Assistant */
.main .block-container {
    padding-left: 4rem !important;
    padding-right: 4rem !important;
    padding-top: 2.5rem !important;
    max-width: 100% !important;
}
.css-18e3th9 {
    padding-left: 0 !important;
    padding-right: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🤖 AI Agents")
st.caption("Collaborate with AI agents using the ReAct pattern to work on code in a sandboxed environment")

# Initialize session state
if 'agent_messages' not in st.session_state:
    st.session_state.agent_messages = []
if 'selected_persona' not in st.session_state:
    st.session_state.selected_persona = "None - Default Agent"
if 'agent_file_content' not in st.session_state:
    st.session_state.agent_file_content = "# This is a test\n"
if 'agent_language' not in st.session_state:
    st.session_state.agent_language = 'python'
if 'agent_is_processing' not in st.session_state:
    st.session_state.agent_is_processing = False
if 'agent_current_file' not in st.session_state:
    st.session_state.agent_current_file = None


def create_new_task():
    """Reset conversation for a new task"""
    st.session_state.agent_messages = []
    st.session_state.agent_is_processing = False


async def process_user_message(user_input: str):
    """
    Process user message through agent loop.
    Adapted from agent-cli/agent-cli.py for Streamlit integration.
    """
    st.session_state.agent_is_processing = True
    
    # Add user message to history
    st.session_state.agent_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Load persona and create system prompt
    try:
        persona_content = load_persona(st.session_state.selected_persona)
        system_prompt = create_agent_system_prompt(persona_content)
    except Exception as e:
        st.session_state.agent_messages.append({
            "role": "error",
            "content": f"Failed to load persona: {str(e)}",
            "timestamp": datetime.now()
        })
        st.session_state.agent_is_processing = False
        return
    
    # Build messages for agent loop
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (excluding status/tool messages for cleaner context)
    for msg in st.session_state.agent_messages:
        if msg["role"] in ["user", "assistant"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Create placeholder for streaming responses
    status_placeholder = st.empty()
    
    assistant_response = ""
    
    try:
        # Stream agent loop responses (ReAct pattern: Think → Act → Observe)
        async for msg_type, content, metadata in agent_loop_streaming(messages):
            if msg_type == "status":
                # Show status updates (agent thinking/acting)
                with status_placeholder:
                    st.info(f"� {content}")
            
            elif msg_type == "tool_result":
                # Check if this is a display_in_editor command (code without saving)
                if content.startswith("DISPLAY_IN_EDITOR:"):
                    # Parse the marker: DISPLAY_IN_EDITOR:language|code
                    parts = content.replace("DISPLAY_IN_EDITOR:", "").split("|", 1)
                    language = parts[0] if len(parts) > 0 else "python"
                    code_content = parts[1] if len(parts) > 1 else ""
                    
                    # Update editor state without saving to file
                    st.session_state.agent_file_content = code_content
                    st.session_state.agent_language = language
                    st.session_state.agent_current_file = None  # No file, just code
                    
                    # Don't add a message - the code is already in the assistant's response
                    
                # Check if this is a load_to_editor command (from saved file)
                elif content.startswith("LOAD_TO_EDITOR:"):
                    # Parse the marker: LOAD_TO_EDITOR:file_path|language|info
                    parts = content.replace("LOAD_TO_EDITOR:", "").split("|")
                    file_path = parts[0]
                    language = parts[1] if len(parts) > 1 else "python"
                    
                    # Load the actual file content
                    from services.agent_tools import get_sandbox_root
                    from pathlib import Path
                    try:
                        sandbox_root = get_sandbox_root()
                        file_full_path = sandbox_root / file_path
                        file_content = file_full_path.read_text(encoding='utf-8')
                        
                        # Update editor state
                        st.session_state.agent_file_content = file_content
                        st.session_state.agent_language = language
                        st.session_state.agent_current_file = file_path
                        
                        # Add success message to chat
                        st.session_state.agent_messages.append({
                            "role": "tool_result",
                            "content": f"✅ Loaded '{file_path}' into the editor ({parts[2] if len(parts) > 2 else 'file loaded'})",
                            "metadata": metadata,
                            "timestamp": datetime.now()
                        })
                    except Exception as e:
                        st.session_state.agent_messages.append({
                            "role": "tool_result",
                            "content": f"❌ Failed to load file: {str(e)}",
                            "metadata": metadata,
                            "timestamp": datetime.now()
                        })
                else:
                    # Regular tool result
                    st.session_state.agent_messages.append({
                        "role": "tool_result",
                        "content": content,
                        "metadata": metadata,
                        "timestamp": datetime.now()
                    })
                
                # Clear status but DON'T rerun - let the agent loop continue!
                # The loop will provide the final assistant response after processing tool results
                status_placeholder.empty()
            
            elif msg_type == "assistant":
                # Final assistant response
                # Check if assistant wants to display code in editor
                if "DISPLAY_IN_EDITOR:" in content:
                    # Extract the marker and code
                    marker_start = content.find("DISPLAY_IN_EDITOR:")
                    marker_end = content.find("\n\n", marker_start) if "\n\n" in content[marker_start:] else len(content)
                    marker_line = content[marker_start:marker_end]
                    
                    # Parse: DISPLAY_IN_EDITOR:language|code
                    parts = marker_line.replace("DISPLAY_IN_EDITOR:", "").split("|", 1)
                    if len(parts) == 2:
                        language = parts[0].strip()
                        code_content = parts[1].strip()
                        
                        # Update editor state
                        st.session_state.agent_file_content = code_content
                        st.session_state.agent_language = language
                        st.session_state.agent_current_file = None  # No file, just code
                    
                    # Remove the marker from the response shown to user
                    assistant_response = content[:marker_start] + content[marker_end:]
                else:
                    assistant_response = content
                    
                status_placeholder.empty()
            
            elif msg_type == "error":
                # Error occurred
                st.session_state.agent_messages.append({
                    "role": "error",
                    "content": content,
                    "timestamp": datetime.now()
                })
                status_placeholder.empty()
                st.session_state.agent_is_processing = False
                st.rerun()
                return
        
        # Add final assistant response
        if assistant_response:
            st.session_state.agent_messages.append({
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now()
            })
    
    except Exception as e:
        # Format error message cleanly without debug info
        error_msg = str(e)
        # Truncate very long error messages
        if len(error_msg) > 500:
            error_msg = error_msg[:500] + "... (error truncated)"
        
        st.session_state.agent_messages.append({
            "role": "error",
            "content": f"❌ Error: {error_msg}",
            "timestamp": datetime.now()
        })
    
    finally:
        st.session_state.agent_is_processing = False
        status_placeholder.empty()
        st.rerun()


# Main layout: Left panel (Chat) + Right panel (Code Editor)
# Ratio adjusted to match reference UI: chat narrower, editor wider
col1, col2 = st.columns([1, 1.8])

# Add aligned headings at the top of both columns
with col1:
    st.subheader("💬 Chat")
with col2:
    st.subheader("📝 Code Editor")

# Left Panel - Chat Interface (Cline-style)
with col1:
    # Reduce spacing with custom CSS and adjust font sizes
    st.markdown("""
    <style>
    .stSelectbox {
        margin-bottom: 0rem !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.5rem !important;
    }
    /* Reduce font size for captions and help text */
    .stCaption {
        font-size: 12px !important;
    }
    /* Slightly smaller selectbox text */
    .stSelectbox label {
        font-size: 13px !important;
    }
    /* Welcome box styling to match reference */
    .welcome-box {
        background-color: #17181c;
        padding: 0.8rem 1.1rem;
        border-radius: 6px;
        border-left: 3px solid #2f73ff;
        font-size: 0.9rem;
        line-height: 1.35;
        margin-bottom: 0.5rem;
    }
    /* Reduce vertical spacing between all elements */
    section[data-testid="stVerticalBlock"] {
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
    }
    /* Reduce spacing around chat input */
    .stChatInput {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }
    /* Reduce spacing around buttons */
    .stButton {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }
    /* File header styling for editor panel */
    .file-header {
        font-weight: 600;
        margin-bottom: 0.3rem;
        font-size: 14px;
    }
    /* Persona row button alignment */
    div[data-testid="column"] button {
        margin-top: 1.85rem !important;
    }
    /* Reduce gap between columns in persona row */
    div[data-testid="column"] {
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
    /* Editor metadata styling */
    .editor-meta {
        font-size: 0.75rem;
        color: #6B6B6B;
        margin-top: 0.2rem;
    }
    /* Micro-styling for typography matching reference */
    label, .stTextInput>div>div>input, .stChatInput>div>div>input {
        font-size: 0.85rem !important;
    }
    /* Make secondary buttons slightly shorter */
    button[kind="secondary"] {
        padding-top: 0.35rem !important;
        padding-bottom: 0.35rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Persona selector - loads from personas directory
    available_personas = get_available_personas()
    
    # Row 1: Label only
    st.markdown("**Select Persona:**")
    
    # Row 2: Dropdown + icon buttons (aligned in same row)
    col_persona, col_info, col_reset = st.columns([8, 1, 1])
    
    with col_persona:
        selected_persona = st.selectbox(
            "Select Persona",
            options=available_personas,
            index=available_personas.index(st.session_state.selected_persona),
            key="persona_selector",
            label_visibility="collapsed"  # No label here - it's in Row 1
        )
        
        if selected_persona != st.session_state.selected_persona:
            st.session_state.selected_persona = selected_persona
            # Don't clear conversation - allow using different personas in same conversation
            st.rerun()
    
    with col_info:
        if st.button("📄", key="persona_info_btn", help="Persona info"):
            pass  # Could show persona details in a modal/expander
    
    with col_reset:
        if st.button("🔄", key="persona_reset_btn", help="Reset persona"):
            st.session_state.selected_persona = "None - Default Agent"
            st.session_state.agent_messages = []
            st.rerun()
    
    # Chat history container with scrolling (tall to match reference UI)
    chat_container = st.container(height=580)
    
    with chat_container:
        if len(st.session_state.agent_messages) == 0:
            # Compact welcome panel matching reference UI
            st.markdown("""
            <div class="welcome-box">
                <b>👋 Welcome!</b><br>
                Start a conversation by typing a message below.<br><br>
                Try commands like:<br>
                • 'List files in the sandbox'<br>
                • 'Create a file hello.py with a greeting function'<br>
                • 'Read test.py into the editor'
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display message history
            for message in st.session_state.agent_messages:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(content)
                
                elif role == "assistant":
                    with st.chat_message("assistant"):
                        st.markdown(content)
                
                elif role == "tool_result":
                    # Tool execution results
                    metadata = message.get("metadata")
                    tool_name = metadata.get("tool", "tool") if metadata else "tool"
                    
                    # Special handling for list_files - show as formatted list
                    if tool_name == "list_files" and content.startswith("Files in"):
                        with st.chat_message("assistant"):
                            # Parse and format the file list
                            lines = content.split('\n')
                            st.markdown(lines[0])  # "Files in .:"
                            for line in lines[1:]:
                                if line.strip().startswith('-'):
                                    # Convert "  - filename" to bullet point
                                    filename = line.strip()[2:]  # Remove "- "
                                    st.markdown(f"• **{filename}**")
                            st.markdown("\n*Let me know if you'd like to open, edit, or perform any other actions on any of these files!*")
                    
                    # Special handling for file loaded messages - show prominently
                    elif content.startswith("✅ Loaded") or content.startswith("❌ Failed"):
                        with st.chat_message("assistant"):
                            st.success(content) if content.startswith("✅") else st.error(content)
                    
                    else:
                        # Hide regular tool results - user should only see final assistant response
                        # Tool results are internal to the agent loop and shouldn't be displayed
                        pass
                
                elif role == "error":
                    with st.chat_message("assistant", avatar="❌"):
                        # Show concise error message
                        error_lines = content.split('\n')
                        # Take only the first line or first 100 characters
                        if len(error_lines) > 0:
                            first_line = error_lines[0]
                            if len(first_line) > 100:
                                concise_error = first_line[:100] + "..."
                            else:
                                concise_error = first_line
                        else:
                            concise_error = "An error occurred"
                        
                        st.error(f"❌ {concise_error}")
    
    # Chat input
    user_input = st.chat_input(
        "Type your message...",
        disabled=st.session_state.agent_is_processing,
        key="agent_chat_input"
    )
    
    if user_input and not st.session_state.agent_is_processing:
        asyncio.run(process_user_message(user_input))
    
    # Create New Task button (full-width to match reference UI)
    if st.button("🆕 Create New Task", type="secondary", key="create_task_btn", use_container_width=True):
        create_new_task()
        st.rerun()
    
    # Show status only when processing
    if st.session_state.agent_is_processing:
        st.caption("🔄 Agent is thinking...")
    else:
        # Tips text at bottom (subtle, gray)
        st.markdown("<p style='font-size: 11px; color: #6B6B6B; margin-top: 0.5rem;'>💡 Tips: Use natural language to ask the agent to work with files in the sandbox</p>", unsafe_allow_html=True)

# Right Panel - Code Editor
with col2:
    # File info and language selector row
    col_file, col_lang = st.columns([2, 1])
    
    with col_file:
        current_file = st.session_state.agent_current_file or "None"
        st.markdown(f"<div class='file-header'>📄 File: {current_file}</div>", unsafe_allow_html=True)
    
    with col_lang:
        language = st.selectbox(
            "Language",
            options=['python', 'javascript', 'typescript', 'java', 'cpp', 'html', 'css', 'json', 'markdown'],
            index=0,
            key="agent_language_selector",
            label_visibility="collapsed"
        )
        if language != st.session_state.agent_language:
            st.session_state.agent_language = language
    
    # Render Monaco editor with reduced top padding
    editor_content = render_code_editor(
        content=st.session_state.agent_file_content,
        language=st.session_state.agent_language,
        height=520,
        editor_mode='user'
    )
    
    # Sync editor content back to session state
    if editor_content is not None and editor_content != st.session_state.agent_file_content:
        st.session_state.agent_file_content = editor_content
    
    # Editor metadata bar
    line_count = len(st.session_state.agent_file_content.split('\n'))
    char_count = len(st.session_state.agent_file_content)
    st.markdown(f"<div class='editor-meta'>{line_count} lines • {char_count} characters • Language: {st.session_state.agent_language}</div>", unsafe_allow_html=True)
