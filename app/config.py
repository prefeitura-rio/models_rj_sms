import os


API_PREFIX = os.environ.get("API_PREFIX", "/api")
PROJECT_NAME = os.environ.get("PROJECT_NAME", "FastAPI")
VERSION = os.environ.get("VERSION", "0.1.0")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
