from pydantic import BaseModel
from typing import Optional, Literal


class MedLMParameters(BaseModel):
    temperature: float
    maxOutputTokens: int
    topK: int
    topP: float

class MedLMInstance(BaseModel):
    content: str

class MedLMInput(BaseModel):
    model: Literal["medlm-large", "medlm-medium"] = "medlm-large"
    instances: list[MedLMInstance]
    parameters: Optional[MedLMParameters]

class MedLMOutput(BaseModel):
    results: dict