import os
import sys
from pathlib import Path

# Add backend directory to sys.path so 'src.main' is importable from root
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Ensure SQLite data directory exists
for path in [Path("/home/site/wwwroot/data"), Path(__file__).resolve().parent / "data"]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

from src.main import app  # noqa: E402
