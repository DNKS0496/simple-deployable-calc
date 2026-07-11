import logging

from sqlalchemy.orm import Session

from app.db_models.calculation import Calculation
from app.business_logic.calculator import CalculationResult


logger = logging.getLogger(__name__)


class CalculationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, result: CalculationResult) -> Calculation:
        logger.debug(
            "Saving calculation result to database: operation=%s",
            result.operation
        )
        calculation = Calculation(
            a = result.a,
            b= result.b,
            operation=result.operation,
            result=result.result
        )

        try:
            self.db.add(calculation)
            self.db.commit()
            self.db.refresh(calculation)

            logger.info(
                "Calculation saved successfully: id=%s operation=%s",
                calculation.id, calculation.operation
            )

            return calculation
        except Exception:
            self.db.rollback()
            logger.exception(
                "Failed to save calculation"
            )
    
    def list_recent(self, limit: int = 50) -> list[Calculation]:
        logger.debug("Fetching recent calculations: limit=%s", limit)

        return (
            self.db.query(Calculation)
            .order_by(Calculation.id.desc())
            .limit(limit)
            .all()
            )
    
    def get_by_id(self, calculation_id: int) -> Calculation | None:
        logger.debug("Fetching calculation by id=%s", calculation_id)

        return (
            self.db.query(Calculation)
            .filter(Calculation.id == calculation_id)
            .first()
        )
    
    def delete_by_id(self, calculation_id: int) -> bool:
        logger.debug("Deleting calculation by id: id=%s", calculation_id)

        calculation = self.get_by_id(calculation_id)

        if calculation is None:
            return False
        
        try:
            self.db.delete(calculation)
            self.db.commit()

            logger.info("Calculation deleted successfully: id=%s", calculation_id)

            return True
        except Exception:
            self.db.rollback()
            logger.exception("Failed to delete calculation: id=%s", calculation_id)
            return False
        