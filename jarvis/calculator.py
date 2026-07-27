from __future__ import annotations

import ast
import math
import operator

_OPERATORS = {
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

_WORDS = {
    "plus": "+",
    "add": "+",
    "minus": "-",
    "subtract": "-",
    "times": "*",
    "multiplied by": "*",
    "multiply": "*",
    "divided by": "/",
    "divide": "/",
    "over": "/",
    "to the power of": "**",
    "squared": "**2",
    "cubed": "**3",
}


def _normalize(expression: str) -> str:
    text = expression.lower()
    for word, symbol in _WORDS.items():
        text = text.replace(word, f" {symbol} ")
    text = text.replace("x", "*") if " x " in f" {text} " else text
    allowed = set("0123456789.+-*/() %")
    text = "".join(char for char in text if char in allowed)
    return " ".join(text.split())


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


def calculate(expression: str) -> str:
    """Safely evaluate a basic arithmetic expression spoken or typed by the user."""
    cleaned = _normalize(expression)
    if not cleaned:
        return "Please give me a valid math expression, sir."
    try:
        tree = ast.parse(cleaned, mode="eval")
        result = _eval_node(tree.body)
        if math.isclose(result, round(result)):
            result_text = str(int(round(result)))
        else:
            result_text = f"{result:.4f}".rstrip("0").rstrip(".")
        return f"The result is {result_text}, sir."
    except ZeroDivisionError:
        return "I cannot divide by zero, sir."
    except Exception:
        return "I could not calculate that, sir. Please try a simpler expression."
