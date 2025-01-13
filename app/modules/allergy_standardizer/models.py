import numpy as np

from pydantic import BaseModel


class AllergyStandardizeInput(BaseModel):
    allergies_list: list[str]

class AllergyStandardizeOutput(BaseModel):
    results: list[dict]
