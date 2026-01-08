#!/bin/bash
# Wasteless UI - Start Script
# ============================

echo "🚀 Starting Wasteless UI..."

# Check if PostgreSQL is running
if ! docker ps | grep -q wasteless-postgres; then
    echo "⚠️  WARNING: PostgreSQL container is not running!"
    echo "   Start it with: cd ../wasteless && docker-compose up -d"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Start Streamlit on port 8888
echo "📊 Starting Streamlit on http://localhost:8888"
streamlit run app.py --server.port 8888 --server.address localhost

# Note: Press Ctrl+C to stop the server
