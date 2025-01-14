import jwt
from datetime import datetime, timedelta
from typing import Annotated
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from fastapi import Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader


from app.config import JWT_SECRET_KEY, JWT_ALGORITHM


security = HTTPBearer()

def generate_token(data: Dict, expires_in: Optional[int] = 60) -> str:
    """
    Generate a JWT token.

    Args:
        data (Dict): The payload to include in the token.
        expires_in (Optional[int]): Token expiration time in minutes. Defaults to 60 minutes.

    Returns:
        str: The generated JWT token.
    """
    expiration = datetime.utcnow() + timedelta(minutes=expires_in)
    payload = {
        **data,
        "exp": expiration,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

