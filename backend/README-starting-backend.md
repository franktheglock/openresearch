# Starting the Backend (Windows)

Use the included `start_backend.bat` to start the FastAPI backend on Windows.

Usage:

```
cd backend
start_backend.bat [port] [--bg] [--reload]
```

Arguments:
- `port` (optional): TCP port to bind the server to. Default: `8000`.
- `--bg` (optional): Start the server in a new window (background).
- `--reload` (optional): Enable `uvicorn --reload` for development.

Examples:
- `start_backend.bat` — Start on default port 8000 in the current window.
- `start_backend.bat 3000` — Start on port 3000.
- `start_backend.bat 8000 --bg` — Start in a new window (background).
- `start_backend.bat 8000 --reload` — Start with autoreload (useful during development).

Notes:
- The script will activate a virtual environment if `venv\Scripts\activate.bat` or `.venv\Scripts\activate.bat` is present.
- If `uvicorn` isn't available as a console script, the script falls back to `python -m uvicorn app.main:app`.
- For production deployment use a process manager or containerization instead of `--bg`.
