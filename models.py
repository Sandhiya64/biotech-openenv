from pydantic import BaseModel
from typing import List, Dict

class BiotechAction(BaseModel):
    action_type: str  # "antibiotic", "antiviral", "test", "wait"


class BiotechObservation(BaseModel):
    symptoms: List[str]
    vitals: Dict[str, float]
    health_score: float
    done: bool
    reward: float


class BiotechState(BaseModel):
    step_count: int
    disease: str
    treated: bool