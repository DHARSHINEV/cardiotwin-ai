"""
Re-export FastAPI app for standard module resolution.
"""
from backend.main import app

__all__ = ["app"]
