"""
AI Code Assistant - Advanced AI-powered code development with Monaco editor integration
"""

import asyncio
import traceback

import streamlit as st

import services.extract
# Import services
from services.llm import create_conversation_starter
from services.prompts import review_prompt, debug_prompt, modify_code_prompt
from ui.interactions import chat_handler

st.set_page_config(page_title="AI Code Assistant", layout="wide")

try:
    from streamlit_monaco import st_monaco
except ImportError:
    st.error("Monaco editor not available. Run: pip install streamlit-monaco")
    st.stop()

# Title and description
st.title("🤖 AI Code Assistant")
st.caption("Advanced AI-powered code development with Monaco editor integration")

# Initialize session state
if 'file_content' not in st.session_state:
    st.session_state.file_content = ""
if 'language' not in st.session_state:
    st.session_state.language = 'python'
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'current_action' not in st.session_state:
    st.session_state.current_action = None
if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False
if 'show_preview' not in st.session_state:
    st.session_state.show_preview = False
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""


def run_llm_query(action_type):
    """
    This function runs a query using the LLM model and updates the code and explanation accordingly.
    """
    # Set streaming state
    st.session_state.is_streaming = True
    st.session_state.current_action = action_type
    st.session_state.explanation = ""
    st.rerun()

def reset_page():
    """
    Reset the page by clearing all session state variables.
    """
    st.session_state.file_content = ""
    st.session_state.language = 'python'
    st.session_state.explanation = ""
    st.session_state.current_action = None
    st.session_state.is_streaming = False
    st.session_state.show_preview = False
    st.session_state.user_input = ""  # Clear the prompt text area
    st.session_state.editor_key += 1  # Force Monaco to refresh
    if 'current_prompt' in st.session_state:
        del st.session_state.current_prompt
    st.rerun()

# Main layout: Left panel (1/3) + Right panel (2/3)
col1, col2 = st.columns([1, 2])

# Left Panel - Input and buttons
with col1:
    # Input area
    user_input = st.text_area(
        "Enter your code request:",
        value=st.session_state.user_input,
        height=100,
        placeholder="e.g., Add error handling, or Fix the bug with division by zero",
        key="user_input_area"
    )

    # Update session state when user types
    if user_input != st.session_state.user_input:
        st.session_state.user_input = user_input

    # Action buttons
    st.caption("**Actions:**")
    col_a, col_b, col_c = st.columns(3)

    # Check if we have input for actions that need it
    has_input = user_input and user_input.strip()

    with col_a:
        review_btn = st.button("👁️ Review", help="Review code for best practices")

    with col_b:
        debug_btn = st.button("🔧 Debug", help="Debug and fix errors")

    with col_c:
        modify_btn = st.button("✏️ Modify", help="Modify code based on request")

    st.divider()

    # Show streaming or explanation response section
    if st.session_state.is_streaming and 'current_prompt' in st.session_state:
        with st.container():
            st.markdown("""
            <div style="background-color: #262730; padding: 15px; border-radius: 10px; border-left: 3px solid #00d4aa;">
            <p style="margin: 0; color: #00d4aa; font-size: 14px;">
                <span style="display: inline-block; width: 12px; height: 12px; border: 2px solid #00d4aa; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px;"></span>
                Streaming response...
            </p>
            </div>
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            </style>
            """, unsafe_allow_html=True)

        # Create streaming container
        stream_container = st.empty()

        print(f"[DEBUG] Starting LLM query for action: {st.session_state.current_action}")
        print(f"[DEBUG] Prompt length: {len(st.session_state.current_prompt)}")

        try:
            # Run the LLM query with streaming
            _, llm_response = asyncio.run(
                chat_handler.run_conversation(
                    create_conversation_starter(st.session_state.current_prompt),
                    stream_container
                )
            )

            print(f"[DEBUG] Full response received, length: {len(llm_response)}")
            print(f"[DEBUG] First 100 chars: {llm_response[:100]}")

            # Extract JSON response with new method
            modified_code, explanation = services.extract.extract_json_response(llm_response)

            print(f"[DEBUG] JSON extraction result - Code: {modified_code is not None}, Explanation: {explanation is not None}")
            if modified_code:
                print(f"[DEBUG] Extracted code length: {len(modified_code)}")
                print(f"[DEBUG] First 50 chars of code: {modified_code[:50]}")
            else:
                print("[DEBUG] No code extracted from response")

            if explanation:
                print(f"[DEBUG] Explanation length: {len(explanation)}")

            # Update session state with extracted content
            if modified_code:
                old_content = st.session_state.file_content or ""
                print(f"[DEBUG] Updating file_content from '{old_content[:30]}...' to '{modified_code[:30]}...'")
                st.session_state.file_content = modified_code
                st.session_state.editor_key += 1  # Force Monaco to recreate with new content
                print(f"[DEBUG] Session state updated with new code. file_content is now {len(st.session_state.file_content)} chars")
                print(f"[DEBUG] Editor key incremented to {st.session_state.editor_key}")

            st.session_state.explanation = services.extract.format_code_explanation(explanation)
            st.session_state.is_streaming = False

            print("[DEBUG] Streaming completed, triggering rerun...")
            st.success(f"✅ {st.session_state.current_action.title()} completed!")
            st.rerun()

        except Exception as e:
            print(f"[ERROR] Exception during streaming: {str(e)}")
            traceback.print_exc()
            st.error(icon="🔥", body=f":red[Error encountered: {e}]")
            st.session_state.explanation = f":red[Error encountered: {e}]"
            st.session_state.is_streaming = False
            st.rerun()

    elif st.session_state.explanation:
        with st.container():
            st.markdown(f"""
            <div style="background-color: #262730; padding: 15px; border-radius: 10px; border-left: 3px solid #00d4aa; color: #ffffff;">
            {st.session_state.explanation}
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️ Clear Response"):
            st.session_state.explanation = ""
            st.rerun()

    # Reset button - always visible
    st.divider()
    if st.button("🔄 Reset Page",
                 type="secondary",
                 help="Clear all content, code, and explanations to start fresh"):
        reset_page()

# Right Panel - Code Editor
with col2:

    # Monaco Editor
    editor_content = st_monaco(
        value=st.session_state.file_content,
        height=500,
        language=st.session_state.language,
        theme="vs-dark"
    )

    # Smart sync: don't let empty editor overwrite AI-generated content
    if editor_content != st.session_state.file_content:
        # If editor is empty but session has content, ignore (Monaco catching up)
        if not editor_content and st.session_state.file_content:
            print(f"[DEBUG] Ignoring empty editor content - Monaco catching up to session state")
        else:
            print(f"[DEBUG] Editor content changed, updating file_content")
            print(f"[DEBUG] Editor: {len(editor_content) if editor_content else 0} chars, Session: {len(st.session_state.file_content)} chars")
            st.session_state.file_content = editor_content

    # Editor stats
    content = st.session_state.file_content or ""
    lines = len(content.splitlines())
    chars = len(content)
    st.caption(f"📏 {lines} lines • {chars} characters • Language: {st.session_state.language}")


# Handle button actions using existing prompt patterns
if review_btn:
    prompt = review_prompt(st.session_state.file_content)
    st.session_state.current_prompt = prompt
    run_llm_query("review")

if debug_btn:
    if has_input:
        prompt = debug_prompt(user_input, st.session_state.file_content)
        st.session_state.current_prompt = prompt
        run_llm_query("debug")
    else:
        st.error("Please enter error description for debugging")

if modify_btn:
    if has_input:
        prompt = modify_code_prompt(user_input, st.session_state.file_content)
        st.session_state.current_prompt = prompt
        run_llm_query("modify")
    else:
        st.error("Please enter modification request")
