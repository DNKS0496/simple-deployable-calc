from logging import getLogger
from dataclasses import dataclass

logger = getLogger(__name__)

@dataclass(frozen=True)
class CalculationInput:
    a: float
    b: float
    operation: str


@dataclass(frozen=True)
class CalculationResult:
    a: float
    b: float
    operation: str
    result: float


def calculate(input_data: CalculationInput) -> CalculationResult:
    operation = input_data.operation.strip().lower()

    logger.debug(
        "Calculating result: a=%s, b=%s, operation=%s",
        input_data.a, input_data.b, operation,
    )
    if operation == "add":
        result = input_data.a + input_data.b
    elif operation == "subtract":
        result = input_data.a - input_data.b
    elif operation == "multiply":
        result = input_data.a * input_data.b
    elif operation == "divide":
        if input_data.b == 0:
            logger.warning("Attempted dividing by zero")
            raise ValueError("Division by zero is not allowed.")
        result = input_data.a / input_data.b
    else:
        logger.warning("Unsupported operation: %s requested", operation)
        raise ValueError("Operation must be one of: add, subtract, multiply, divide.")
    
    logger.info("Calculation completed successfully: operation=%s", operation)

    return CalculationResult(
        a=input_data.a,
        b=input_data.b,
        operation=operation,
        result=result
    )