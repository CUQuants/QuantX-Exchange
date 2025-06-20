#!/usr/bin/env python3
"""
CU Quants Exchange Startup Script
Run this to start the CQAF trading exchange
"""

import uvicorn
import sys
import os

def main():
    print("🚀 Starting CU Quants Exchange...")
    print("📊 Symbol: CQAF (CU Quants Attendance Futures)")
    print("🌐 Web Interface: http://localhost:8000")
    print("📡 WebSocket: ws://localhost:8000/ws")
    print("📖 API Docs: http://localhost:8000/docs")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Exchange shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting exchange: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()