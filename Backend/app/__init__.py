"""Make the app directory a package so it can be imported as 'app'.

This file can stay empty; it's present to ensure imports like
`import app.main` work reliably when running uvicorn.
"""

__all__ = ["main", "config", "database", "models", "schemas", "security", "routers"]
