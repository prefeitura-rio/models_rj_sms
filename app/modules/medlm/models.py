from typing import Optional, Literal, List
from pydantic import BaseModel, Field


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

class SafetyAttributes(BaseModel):
    categories: List[str]
    blocked: bool
    scores: List[float]

class CitationMetadata(BaseModel):
    citations: List[str] = Field(default_factory=list)

class Prediction(BaseModel):
    safetyAttributes: SafetyAttributes
    content: str
    citationMetadata: CitationMetadata

class TokenCount(BaseModel):
    totalBillableCharacters: int
    totalTokens: int

class TokenMetadata(BaseModel):
    outputTokenCount: TokenCount
    inputTokenCount: TokenCount

class Metadata(BaseModel):
    tokenMetadata: TokenMetadata

class MedLMOutput(BaseModel):
    predictions: List[Prediction]
    metadata: Metadata