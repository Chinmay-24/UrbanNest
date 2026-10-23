import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "urbannest-college-dev-key")

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
POSTGRES_DATABASE = os.environ.get("POSTGRES_DATABASE", "urbannest")
