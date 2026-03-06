# AI Development Assistant

A Python-based AI development tool featuring intelligent chat, requirements engineering, code assistance, and autonomous agents. This system integrates multiple LLM-powered capabilities through a modular architecture with persona-based interactions and real-time streaming responses.

## Features

- Interactive Chat Interface: Streaming LLM responses with conversation history and context management
- Requirements Engineering: Automated generation of business documents, vision statements, and project plans
- Code Assistant: Integrated code review, debugging, and modification with Monaco editor
- Autonomous Agents: ReAct-pattern agents with tool integration and 9 specialized personas
- Learning Topics: AI-powered explanations and educational content generation

## Technical Highlights

### Architecture

**Service Layer Pattern**
- Separation of business logic from UI components
- Modular prompt engineering with centralized templates
- Reusable service modules for LLM interactions, embeddings, and agent workflows

**Agent System**
- ReAct (Reasoning + Acting) pattern implementation
- Tool abstraction layer supporting file operations, web search, and calculations
- Persona-based system prompts for specialized agent behaviors

**Streaming Implementation**
- Real-time token streaming from OpenAI-compatible APIs
- Async/await patterns for non-blocking UI updates
- Session state management for conversation persistence

### Technology Stack

- Framework: Streamlit (Python web framework)
- LLM Integration: OpenAI API (compatible with Azure OpenAI, Ollama, LM Studio)
- Embeddings: sentence-transformers (local) or OpenAI API
- Code Editor: streamlit-monaco
- Containerization: Docker with UV package manager
- Dependencies: 93 packages including PyTorch, transformers, and pandas

## Setup

```bash
# Clone repository
git clone https://github.com/pranayds/ai-development-assistant.git
cd ai-development-assistant

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run application
uv run streamlit run 🏠_Home.py
```

Access at `http://localhost:8501`

### Docker Deployment

```bash
docker build -t ai-dev-assistant .
docker run -p 8501:8501 ai-dev-assistant
```

## Configuration

The `.env` file supports multiple LLM providers:

- OpenAI: Standard OpenAI API
- Azure OpenAI: Enterprise Azure deployment
- Local Models: Ollama, LM Studio, or other OpenAI-compatible endpoints

Embedding options include local sentence-transformers or OpenAI API.

## Project Structure

```
ai-development-assistant/
├── 🏠_Home.py                  # Application entry point
├── pages/                      # Streamlit page modules
│   ├── 1_💬_Quick_Chat.py
│   ├── 2_🎓_Learning_Topics.py
│   ├── 3_📓_Requirements.py
│   ├── 4_🔧_AI_Code_Assistant.py
│   └── 6_🤖_AI_Agents.py
├── services/                   # Business logic layer
│   ├── agent_loop.py          # ReAct agent implementation
│   ├── agent_tools.py         # Tool definitions and schemas
│   ├── llm.py                 # LLM API integration
│   ├── personas.py            # Persona management
│   └── prompts.py             # Prompt templates
├── ui/                        # UI components
│   ├── components/            # Reusable Streamlit components
│   └── interactions/          # User interaction handlers
├── personas/                  # Persona definitions (9 specialized agents)
├── data/                      # Data storage and sandbox
└── pyproject.toml            # Python dependencies