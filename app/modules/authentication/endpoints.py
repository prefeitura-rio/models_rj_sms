import json
import requests

from fastapi import APIRouter, HTTPException

from app.modules.authentication.models import LoginInput, LoginOutput
from app.modules.authentication.config import LOGIN_API_URL, TOKEN_EXPIRES_IN
from app.utils.authentication import generate_token


router = APIRouter()


@router.post("/login", tags=["authentication"])
async def login(
    credentials: LoginInput
) -> LoginOutput:
    
    try:
        result = requests.post(
            url=f'{LOGIN_API_URL}/auth/token',
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                'username': credentials.username, 
                'password': credentials.password
            },
            timeout=90
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=408,
            detail={
                "login_api_status_code": None,
                "login_api_result": "Timeout",
            }
        )
    
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "login_api_status_code": result.status_code,
                "login_api_result": result.json()
            }
        )
    
    token = generate_token(
        data = {
            'username': credentials.username,
        },
        expires_in=TOKEN_EXPIRES_IN
    )

    return LoginOutput(
        access_token=token,
        token_type='Bearer',
        token_expire_minutes=TOKEN_EXPIRES_IN,
    )


