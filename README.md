# 🤖 AI Development Assistant

A comprehensive AI-powered development assistant built with Streamlit, featuring intelligent chat, requirements engineering, code assistance, and autonomous AI agents with persona-based interactions.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

## 🌟 Features

- **💬 AI Chat** - Interactive chat with streaming responses and context awareness
- **📓 Requirements Engineering** - Generate business documents, vision statements, and project plans
- **🤖 Code Assistant** - Code review, debugging, and modification with Monaco editor
- **🤖 AI Agents** - Autonomous agents with 9 personas (Professional, Creative, Teacher, etc.) and tool integration

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/ai-development-assistant.git
cd ai-development-assistant
uv sync
cp .env.example .env  # Add your OpenAI API key

# Run
uv run streamlit run 🏠_Home.py
# Open http://localhost:8501

# Or use Docker
docker build -t ai-dev-assistant .
docker run -p 8501:8501 ai-dev-assistant
```

## 📁 Project Structure

```
ai-development-assistant/
├── 🏠_Home.py                      # Main application entry point
├── pages/                          # Streamlit pages
├── services/                       # Business logic layer
├── ui/                            # UI components
├── personas/                      # Persona definitions
├── data/                          # Data storage
├── .env.example                   # Environment template
├── .gitignore                     # Git exclusions
├── Dockerfile                     # Container configuration
├── pyproject.toml                 # Python dependencies
└── README.md                      # This file
```

## 🔧 Configuration

Configure `.env` with your API credentials. Supports OpenAI, Azure OpenAI, and local models (Ollama, LM Studio).

## 🏗️ Architecture

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **LLM Integration**: OpenAI-compatible APIs
- **Embeddings**: sentence-transformers (local) or OpenAI API
- **Code Editor**: streamlit-monaco
- **Containerization**: Docker
- **Package Management**: UV (fast Python package manager)

### Key Design Patterns

- **Service Layer**: Business logic separated from UI
- **Component-Based UI**: Reusable Streamlit components
- **Streaming Responses**: Real-time LLM output streaming
- **State Management**: Streamlit session state for conversation history
- **Modular Prompts**: Centralized prompt engineering
- **Tool Abstraction**: Pluggable agent tools

---

**Built with Python, Streamlit, and OpenAI APIs**