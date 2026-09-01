import pytest

from core.exceptions import ToolExecutionError
from tools.calculator import CalculatorTool
from tools.tool_selector import ToolSelector


def test_calculator_basic_arithmetic():
    calc = CalculatorTool()
    assert calc.calculate("2 + 2") == "Result: 4"
    assert calc.calculate("10 * (3 + 2)") == "Result: 50"
    assert calc.calculate("2 ** 8") == "Result: 256"


def test_calculator_division_by_zero_raises_tool_error():
    calc = CalculatorTool()
    with pytest.raises(ToolExecutionError):
        calc.calculate("1 / 0")


def test_calculator_blocks_code_injection():
    """
    The original implementation used Python's eval() directly, which
    (had ToolSelector's regex filter ever been bypassed, e.g. via a
    future refactor or a different caller) could execute arbitrary
    code. The AST-based evaluator now rejects anything that isn't a
    numeric literal + basic arithmetic operator, by construction.
    """
    calc = CalculatorTool()

    dangerous_inputs = [
        "__import__('os').system('echo pwned')",
        "open('/etc/passwd').read()",
        "().__class__.__bases__",
    ]

    for expression in dangerous_inputs:
        with pytest.raises((ToolExecutionError,)):
            calc.calculate(expression)


def test_calculator_empty_expression_raises():
    calc = CalculatorTool()
    with pytest.raises(ToolExecutionError):
        calc.calculate("")


def test_tool_selector_routes_calculator_query():
    selector = ToolSelector()
    result = selector.execute("calculate 5 + 5")
    assert "10" in result


def test_tool_selector_empty_query_raises():
    selector = ToolSelector()
    with pytest.raises(ToolExecutionError):
        selector.execute("")
