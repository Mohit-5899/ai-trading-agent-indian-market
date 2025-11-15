#!/usr/bin/env python3
"""
Start Live Trading Dashboard
Launches both FastAPI backend and Streamlit frontend
"""

import subprocess
import threading
import time
import sys
from pathlib import Path

def start_backend():
    """Start FastAPI backend server"""
    print("🚀 Starting FastAPI backend...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:api_app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Backend stopped by user")

def start_frontend():
    """Start Streamlit frontend"""
    print("📊 Starting Streamlit dashboard...")
    frontend_path = Path("frontend/dashboard.py")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(frontend_path),
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Frontend stopped by user")

def main():
    """Main function to start both servers"""
    print("="*60)
    print("🤖 AI Trading System - Live Dashboard Launcher")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found. Please run from project root directory.")
        sys.exit(1)
    
    if not Path("frontend/dashboard.py").exists():
        print("❌ Error: frontend/dashboard.py not found.")
        sys.exit(1)
    
    print("✅ Starting AI Trading System...")
    print("📍 Backend will be available at: http://localhost:8000")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("🔄 Auto-refresh: Every 5 seconds")
    print("-" * 60)
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Wait a moment for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Start frontend in main thread
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AI Trading System...")
        print("👋 Thank you for using AI Trading System!")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()