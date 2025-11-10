#!/usr/bin/env python3
"""
Launch script for the Streamlit dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard"""
    
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(current_dir, "dashboard.py")
    
    # Check if dashboard.py exists
    if not os.path.exists(dashboard_path):
        print("❌ Error: dashboard.py not found!")
        return
    
    print("🚀 Starting AI Trading System Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🔧 Make sure your FastAPI backend is running at: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 60)
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

if __name__ == "__main__":
    main()