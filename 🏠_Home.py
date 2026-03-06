import streamlit as st
from dotenv import load_dotenv

from ui.components import sidebar


st.set_page_config(
    page_title="AI Dev Assistant",
    page_icon="🤖",
    layout="wide"
)


sidebar.render_sidebar()

st.toast("Welcome to AI Development Assistant!", icon="🤖")

st.markdown("Welcome to AI Development Assistant, your AI-powered software development companion!")
st.write("Built to help you deliver software faster and better with intelligent AI assistance.")
