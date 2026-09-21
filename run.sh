#!/usr/bin/env bash
set -e

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "No .env found — copying .env.example. Add your ANTHROPIC_API_KEY before running."
    cp .env.example .env
fi

streamlit run app/main.py