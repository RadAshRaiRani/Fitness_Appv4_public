# 🏋️ Agentic Fitness App

An AI-powered fitness application that provides personalized workout and diet recommendations using an agentic architecture with RAG (Retrieval Augmented Generation) systems.

## ✨ Features

- 🤖 **AI Agents**: Supervisor agent coordinates diet and exercise agents for personalized recommendations
- 📚 **RAG Systems**: Document-based knowledge retrieval for diet and exercise information
- 🖼️ **Body Type Classification**: Identify body types (endomorph, ectomorph, mesomorph)
- 💪 **Personalized Plans**: Generate 4-week fitness plans based on body type and goals
- 🔍 **Web Search**: Real-time information retrieval for current fitness trends
- 🔐 **Authentication**: Secure user authentication with Clerk
- 📱 **Modern UI**: Beautiful, responsive frontend built with Next.js

## 🏗️ Architecture

```
┌─────────────────┐
│   Next.js       │
│   Frontend      │
└────────┬────────┘
         │
         │ REST API
         │
┌────────▼─────────────────┐
│      FastAPI Backend     │
│  ┌──────────────────┐    │
│  │  Supervisor      │    │
│  │     Agent        │    │
│  └──────┬───────────┘    │
│         │ Delegates       │
│  ┌──────▼────────────┐   │
│  │  Diet Agent      │   │
│  │  Exercise Agent  │   │
│  └──────┬────────────┘   │
│         │                 │
│  ┌──────▼────────────┐   │
│  │  RAG Systems      │   │
│  │  (Diet + Exercise)│   │
│  └───────────────────┘    │
└───────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Clerk Account ([Sign up here](https://clerk.com)) - Optional for basic testing

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

Backend will run on **http://localhost:8000**

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local and add your Clerk keys and API URL
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

Frontend will run on **http://localhost:3000**

## 📁 Project Structure

```
Agentic_fitnessv2/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── services/        # Business logic (agents, RAG)
│   │   ├── models/          # Database models
│   │   └── main.py          # FastAPI application
│   ├── data/
│   │   ├── diet_documents/  # Diet PDFs (add your own)
│   │   ├── exercise_documents/ # Exercise PDFs (add your own)
│   │   ├── diet_vectors/    # Generated vectors (auto-created)
│   │   └── exercise_vectors/ # Generated vectors (auto-created)
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
│
├── frontend/
│   ├── app/                 # Next.js app directory
│   ├── lib/                 # Utilities
│   ├── package.json         # Node dependencies
│   └── .env.example         # Environment variables template
│
└── README.md               # This file
```

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
OPENAI_API_KEY=sk-your-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend Environment Variables

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
CLERK_SECRET_KEY=sk_test_xxxxx
```

## 📚 RAG Systems

The app includes two RAG systems for knowledge retrieval:

1. **Diet RAG**: Retrieves information from diet/nutrition documents
2. **Exercise RAG**: Retrieves information from exercise/workout documents

### Adding Documents

1. Place PDF files in:
   - `backend/data/diet_documents/` for diet documents
   - `backend/data/exercise_documents/` for exercise documents

2. Process the documents:
   ```bash
   # Using the API
   curl -X POST "http://localhost:8000/rag/diet/process-folder"
   curl -X POST "http://localhost:8000/rag/exercise/process-folder"
   ```

3. Search the documents:
   ```bash
   curl "http://localhost:8000/rag/diet/search?query=protein%20intake&k=3"
   ```

## 🤖 AI Agents

The application uses a multi-agent system:

- **Supervisor Agent**: Coordinates the workflow and delegates tasks
- **Diet Agent**: Generates personalized diet recommendations using RAG
- **Exercise Agent**: Generates personalized workout plans using RAG

### Generate Recommendations

```bash
curl -X POST "http://localhost:8000/agents/recommendations/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "body_type": "endomorph",
    "goals": "lose weight",
    "max_iterations": 2
  }'
```

## 🧪 Testing

### Backend Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Tech Stack

### Backend
- FastAPI (Python web framework)
- LangChain (Agent orchestration)
- FAISS (Vector search)
- Sentence Transformers (Embeddings)
- SQLite (Local database)

### Frontend
- Next.js 16 (React framework)
- TypeScript
- Tailwind CSS
- Clerk (Authentication)

## 📝 Development

### Backend Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run server
uvicorn app.main:app --reload

# Install new package
pip install <package>
pip freeze > requirements.txt
```

### Frontend Commands

```bash
# Development
npm run dev

# Production build
npm run build
npm run start

# Lint
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License

## 🙏 Acknowledgments

- OpenAI for GPT models
- LangChain for agent framework
- Clerk for authentication
- FastAPI and Next.js communities

---

**Happy coding! 🚀**
