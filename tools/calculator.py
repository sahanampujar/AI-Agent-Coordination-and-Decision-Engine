import ast
import operator

from core.exceptions import ToolExecutionError


# ============================================================
# SAFE ARITHMETIC EVALUATION
# ============================================================
#
# The original implementation used Python's built-in eval() directly
# on user-supplied text:
#
#     result = eval(expression)
#
# Even though ToolSelector pre-filters the input with a regex, eval()
# is unsafe by construction and is flagged by any security review.
# This replaces it with an AST-based evaluator that only allows
# numeric literals and the +, -, *, /, //, %, ** operators -- no
# names, attributes, calls, or imports can ever be evaluated.
# ============================================================

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed.")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Operator not allowed: {op_type.__name__}")
        return _ALLOWED_OPERATORS[op_type](
            _safe_eval(node.left),
            _safe_eval(node.right),
        )

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Operator not allowed: {op_type.__name__}")
        return _ALLOWED_OPERATORS[op_type](_safe_eval(node.operand))

    raise ValueError(f"Unsupported expression: {type(node).__name__}")


class CalculatorTool:
    """
    Safe calculator tool for arithmetic operations. Never uses eval().
    """

    def calculate(self, expression):
        try:
            expression = expression.strip()

            if not expression:
                raise ToolExecutionError(
                    "Calculator Tool", "No expression provided."
                )

            tree = ast.parse(expression, mode="eval")
            result = _safe_eval(tree)

            return f"Result: {result}"

        except ZeroDivisionError:
            raise ToolExecutionError("Calculator Tool", "Division by zero.")

        except ToolExecutionError:
            raise

        except Exception as e:
            raise ToolExecutionError("Calculator Tool", str(e))
