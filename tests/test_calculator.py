import pytest

from app.business_logic.calculator import CalculationInput, calculate


def test_addition():
    result = calculate(
        CalculationInput(a=10, b=5, operation="add")
    )

    assert result.result == 15
    assert result.operation == "add"


def test_subtraction():
    result = calculate(
        CalculationInput(a=10, b=5, operation="subtract")
    )

    assert result.result == 5


def test_multiplication():
    result = calculate(
        CalculationInput(a=10, b=5, operation="multiply")
    )

    assert result.result == 50


def test_division():
    result = calculate(
        CalculationInput(a=10, b=5, operation="divide")
    )

    assert result.result == 2


def test_division_by_zero_raises_error():
    with pytest.raises(ValueError, match="Division by zero"):
        calculate(
            CalculationInput(a=10, b=0, operation="divide")
        )


def test_unsupported_operation_raises_error():
    with pytest.raises(ValueError, match="Operation must be one of"):
        calculate(
            CalculationInput(a=10, b=5, operation="power")
        )