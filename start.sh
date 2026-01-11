#!/bin/bash
# Start Wasteless UI with Streamlit

cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with database credentials"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed!"
    echo "Please install dependencies: pip install -r requirements.txt"
    exit 1
fi

echo "🚀 Starting Wasteless UI on http://localhost:8888"

# Start Streamlit (no need to export env vars, load_dotenv handles it)
streamlit run app.py \
    --server.port 8888 \
    --server.address localhost \
    --server.headless true \
    --server.runOnSave true \
    --client.toolbarMode minimal
