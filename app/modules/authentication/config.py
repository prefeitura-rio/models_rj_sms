import os


LOGIN_API_URL = os.environ.get("LOGIN_API_URL")
TOKEN_EXPIRES_IN = int(os.environ.get("TOKEN_EXPIRES_IN", 60))