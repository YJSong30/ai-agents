from pydantic import BaseModel

class Evaluation(BaseModel):
    """response format for evaluation."""
    score: float
    feedback: str
    is_acceptable: bool