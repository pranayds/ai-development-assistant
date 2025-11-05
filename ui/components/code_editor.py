"""
Code Editor Component - Monaco editor wrapper with state management
"""

import streamlit as st

try:
    from streamlit_monaco import st_monaco
except ImportError:
    st_monaco = None


def render_code_editor(
    content: str,
    language: str = 'python',
    height: int = 500,
    editor_mode: str = 'user'
) -> str:
    """
    Render a Monaco code editor with live statistics and mode indicator.

    Args:
        content: Initial content to display in the editor
        language: Programming language for syntax highlighting (default: 'python')
        height: Editor height in pixels (default: 500)
        editor_mode: Current editor mode - 'user' or 'ai_updating' (default: 'user')

    Returns:
        Current editor content (may differ from initial content if user typed)

    Note:
        This component uses lazy sync - editor content is NOT automatically
        written to session state on every keystroke. The caller should sync
        the returned content to session state only when needed (e.g., before
        running AI actions) to prevent unnecessary reruns.
    """

    if st_monaco is None:
        st.error("Monaco editor not available. Run: pip install streamlit-monaco")
        return content

    # Render Monaco editor
    # Monaco maintains its own internal state between reruns
    editor_content = st_monaco(
        value=content,
        height=height,
        language=language,
        theme="vs-dark"
    )

    # Log content changes for debugging (but don't sync to prevent reruns)
    if editor_mode == 'user':
        if editor_content is not None and editor_content != content:
            if not editor_content and content:
                print(f"[CodeEditor] Monaco initializing - editor empty, session has content")
            else:
                editor_len = len(editor_content) if editor_content else 0
                content_len = len(content) if content else 0
                print(f"[CodeEditor] Content changed - Editor: {editor_len} chars, Passed: {content_len} chars")
    else:
        print(f"[CodeEditor] Mode: '{editor_mode}' - AI is updating")

    # Render statistics and mode indicator
    _render_editor_stats(editor_content or content, language, editor_mode)

    return editor_content


def _render_editor_stats(content: str, language: str, editor_mode: str):
    """
    Render editor statistics and mode indicator below the editor.

    Args:
        content: Current editor content for calculating stats
        language: Programming language name
        editor_mode: Current mode ('user' or 'ai_updating')
    """
    # Calculate stats from current content
    lines = len(content.splitlines()) if content else 0
    chars = len(content) if content else 0

    # Create two columns: stats on left, mode indicator on right
    stats_col, mode_col = st.columns([3, 1])

    with stats_col:
        st.caption(f"📏 {lines} lines • {chars} characters • Language: {language}")

    with mode_col:
        if editor_mode == 'user':
            st.caption("✏️ :green[User Editing]")
        else:
            st.caption("🤖 :orange[AI Updating]")
