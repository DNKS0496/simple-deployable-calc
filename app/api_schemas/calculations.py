from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CalculationCreateRequest(BaseModel):
    a: float
    b: float
    operation: str = Field(
        examples=['add', 'subtract', 'multiply', 'divide']
    )


class CalculationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    a: float
    b: float
    operation: str
    result: float
    created_at: datetime