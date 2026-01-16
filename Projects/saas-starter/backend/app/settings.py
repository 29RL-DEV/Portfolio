import os
from dotenv import load_dotenv

load_dotenv()

# Legacy/local settings file kept for compatibility. Prefer `config.settings`.
# Read values from environment to avoid committing secrets.
SECRET_KEY = os.getenv('SECRET_KEY', '')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

