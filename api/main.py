import os, sys

# Add the backend app directory to PYTHONPATH so we can import the existing FastAPI app
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))
sys.path.insert(0, BASE_DIR)

# Import the FastAPI `app` defined in `backend/app/main.py`
from main import app  # noqa: F401
