import sys
import os
from pathlib import Path

# Setup PYTHONPATH for Vercel Serverless environment
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "python_backend"
app_dir = backend_dir / "app"

for d in [str(app_dir), str(backend_dir), str(root_dir)]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from python_backend.app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    app = FastAPI(title="Agentic-Eval Vercel Gateway Fallback")

    @app.get("/{full_path:path}")
    def fallback(full_path: str):
        return HTMLResponse(f"<h1>Agentic-Eval Gateway</h1><p>Initialization Warning: {e}</p>")
