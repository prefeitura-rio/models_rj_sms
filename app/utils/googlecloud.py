from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

from app.config import SMS_SERVICE_ACCOUNT_FILE


def get_access_token() -> str:
    # Carregar credenciais da conta de serviço
    credentials = Credentials.from_service_account_file(
        SMS_SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    return credentials.token
