#!/usr/bin/env python3
"""
Simple script to run the FastAPI server
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Fakarni Backend Server...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("🔄 Auto-reload enabled")
    print("Press Ctrl+C to stop")
    print("-" * 50)

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )