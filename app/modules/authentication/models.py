import numpy as np

from pydantic import BaseModel


class LoginInput(BaseModel):
    username: str
    password: str

class LoginOutput(BaseModel):
    access_token: str
    token_type: str
    token_expire_minutes: int