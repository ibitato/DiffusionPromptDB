#!/usr/bin/env python3
"""
API Server Launcher

Starts the FastAPI server correctly with proper module imports.
"""

import sys
from pathlib import Path

# Add parent directory to Python path
api_dir = Path(__file__).parent
src_dir = api_dir.parent
sys.path.insert(0, str(src_dir))

# Now import and run
if __name__ == "__main__":
    import uvicorn
    from api.main import app
    from api.config import settings
    
    print("="*70)
    print("DiffusionPromptDB API Server")
    print("="*70)
    print(f"\nStarting server on {settings.host}:{settings.port}")
    print(f"Docs: http://localhost:{settings.port}/docs")
    print(f"ReDoc: http://localhost:{settings.port}/redoc")
    print("\nPress CTRL+C to stop")
    print("="*70)
    print()
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
