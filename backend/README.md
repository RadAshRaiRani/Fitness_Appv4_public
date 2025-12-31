# Backend - FastAPI Application

FastAPI backend with RAG systems and AI agents for fitness recommendations.

## Quick Start

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Start server:**
   ```bash
   uvicorn app.main:app --reload
   ```

Server runs on **http://localhost:8000**

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── agents.py    # Agent endpoints
│   │   ├── rag.py       # RAG endpoints
│   │   ├── classify.py  # Classification endpoints
│   │   └── users.py     # User endpoints
│   ├── services/        # Business logic
│   │   ├── diet_rag.py           # Diet RAG system
│   │   ├── exercise_rag.py       # Exercise RAG system
│   │   ├── supervisor_agent.py   # Supervisor agent
│   │   ├── diet_agent.py          # Diet agent
│   │   ├── exercise_agent.py      # Exercise agent
│   │   └── rag_manager.py          # RAG manager
│   ├── models/          # Database models
│   ├── database.py      # Database setup
│   └── main.py          # FastAPI application
├── data/
│   ├── diet_documents/     # Add diet PDFs here
│   ├── exercise_documents/  # Add exercise PDFs here
│   ├── diet_vectors/        # Generated vectors (auto)
│   └── exercise_vectors/    # Generated vectors (auto)
└── requirements.txt     # Dependencies
```

## API Endpoints

- **Health Check**: `GET /health`
- **RAG Search**: `GET /rag/diet/search?query=...`
- **Process Documents**: `POST /rag/diet/process-folder`
- **Generate Recommendations**: `POST /agents/recommendations/generate`
- **API Docs**: http://localhost:8000/docs

## Environment Variables

See `.env.example` for required variables:
- `OPENAI_API_KEY` - Required for AI agents
- `CORS_ORIGINS` - Allowed frontend origins

## Adding RAG Documents

1. Place PDF files in `data/diet_documents/` or `data/exercise_documents/`
2. Process: `POST /rag/{diet|exercise}/process-folder`
3. Search: `GET /rag/{diet|exercise}/search?query=...`

## Common Commands

```bash
# Run server
uvicorn app.main:app --reload

# Install package
pip install <package>
pip freeze > requirements.txt
```
