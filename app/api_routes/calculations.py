import logging

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api_schemas.calculations import (
    CalculationCreateRequest,
    CalculationResponse
    )
from app.business_logic.calculator import CalculationInput, calculate
from app.data_access.calculation_repository import CalculationRepository
from app.database import get_db
from app.security import require_api_key


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/calculations",
    tags=["calculations"],
    dependencies=[Depends(require_api_key)],
)

@router.post("", response_model=CalculationResponse)
def create_calculation(
    payload: CalculationCreateRequest,
    db: Annotated[Session, Depends(get_db)],
):
    logger.debug("Received create calculation request")
    input_data = CalculationInput(
        a=payload.a,
        b=payload.b,
        operation=payload.operation,
    )
    try:
        result = calculate(input_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    repository = CalculationRepository(db)
    return repository.save(result)


@router.get("", response_model=list[CalculationResponse])
def list_calculations(db: Annotated[Session, Depends(get_db)]):
    repository = CalculationRepository(db)
    return repository.list_recent(limit=50)


@router.get("/{calculation_id}", response_model=CalculationResponse)
def get_calculation(calculation_id: int, db: Annotated[Session, Depends(get_db)]):
    repository = CalculationRepository(db)
    calculation = repository.get_by_id(calculation_id)

    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@router.delete("/{calculation_id}")
def delete_calculation(calculation_id: int, db: Annotated[Session, Depends(get_db)]):
    repository = CalculationRepository(db)
    deleted = repository.delete_by_id(calculation_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    return {"message": "Calculation deleted successfully"}

