from pydantic import BaseModel


class AllergyStandardizeInput(BaseModel):
    allergies_list: list[str]

class Correction(BaseModel):
    input: str
    output: str
    output_medlm_flag: int
    output_medlm_motivo: str

class AllergyStandardizeOutput(BaseModel):
    corrections: list[Correction]


# ----------------
# Models CrewAI
# ----------------
class Item(BaseModel):
    input: str
    output: str

class DataList(BaseModel):
    correcoes: list[Item]

