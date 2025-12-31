#!/bin/bash
# Quick script to check if FastAPI server is running

echo "Checking FastAPI server status..."
echo ""

# Check if port 8000 is listening
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Server is running on port 8000"
    echo ""
    echo "Testing endpoints:"
    echo ""
    echo "1. Health check:"
    curl -s http://localhost:8000/health | python3 -m json.tool
    echo ""
    echo "2. Root endpoint:"
    curl -s http://localhost:8000/
    echo ""
    echo ""
    echo "🌐 Open in browser:"
    echo "   - Swagger UI: http://localhost:8000/docs"
    echo "   - ReDoc: http://localhost:8000/redoc"
else
    echo "❌ Server is NOT running"
    echo ""
    echo "To start the server, run:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   uvicorn app.main:app --reload"
fi

