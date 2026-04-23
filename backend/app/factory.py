"""Expose app instance for Flask CLI (e.g. flask db)."""
from app import create_app

app = create_app()
