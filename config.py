import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "urbannest-college-dev-key")

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "urbannest")
