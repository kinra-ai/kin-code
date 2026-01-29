"""Safe math calculator tool using simpleeval for expression evaluation."""

from __future__ import annotations

from collections.abc import AsyncGenerator
import math
from typing import ClassVar

from pydantic import BaseModel, Field
from simpleeval import InvalidExpression, NameNotDefined, SimpleEval

from kin_code.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    InvokeContext,
    ToolError,
    ToolPermission,
)
from kin_code.core.tools.ui import ToolCallDisplay, ToolResultDisplay, ToolUIData
from kin_code.core.types import ToolCallEvent, ToolResultEvent, ToolStreamEvent

_MAX_EXPONENT = 1000


def _safe_pow(base: float, exp: float) -> float:
    """Safe power function with exponent limit to prevent memory exhaustion."""
    if abs(exp) > _MAX_EXPONENT:
        raise ValueError(f"Exponent magnitude exceeds limit of {_MAX_EXPONENT}")
    return pow(base, exp)


class CalculatorConfig(BaseToolConfig):
    """Configuration for the calculator tool."""

    permission: ToolPermission = ToolPermission.ALWAYS
    precision: int = Field(default=10, description="Decimal precision for results")


class CalculatorArgs(BaseModel):
    """Arguments for the calculator tool."""

    expression: str = Field(description="Mathematical expression to evaluate")


class CalculatorResult(BaseModel):
    """Result from the calculator tool."""

    expression: str
    result: float
    formatted: str


class Calculator(
    BaseTool[CalculatorArgs, CalculatorResult, CalculatorConfig, BaseToolState],
    ToolUIData[CalculatorArgs, CalculatorResult],
):
    """Safely evaluate mathematical expressions."""

    description: ClassVar[str] = """Evaluate mathematical expressions safely.

USE WHEN:
- Calculating numeric values during problem-solving
- Converting units or computing ratios
- Performing arithmetic that needs precision

DO NOT USE WHEN:
- You can easily calculate in your head
- The math is trivial (2+2, simple percentages)

SUPPORTED:
- Arithmetic: +, -, *, /, **, %
- Functions: sin, cos, tan, sqrt, log, exp, abs, pow, floor, ceil
- Constants: pi, e, tau

EXAMPLES:
- "sqrt(2) * 100" - Calculate square root
- "sin(pi/4)" - Trigonometry
- "2**10" - Exponentiation"""

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, CalculatorArgs):
            return ToolCallDisplay(summary="Invalid arguments")
        return ToolCallDisplay(summary=f"Calculating: {event.args.expression}")

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, CalculatorResult):
            return ToolResultDisplay(success=True, message="Success")
        return ToolResultDisplay(
            success=True,
            message=f"{event.result.expression} = {event.result.formatted}",
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Calculating"

    def _create_evaluator(self) -> SimpleEval:
        """Create a configured SimpleEval instance with math functions and constants."""
        evaluator = SimpleEval()
        evaluator.functions.update({
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "exp": math.exp,
            "abs": abs,
            "pow": _safe_pow,
            "floor": math.floor,
            "ceil": math.ceil,
            "round": round,
            "min": min,
            "max": max,
        })
        evaluator.names.update({"pi": math.pi, "e": math.e, "tau": math.tau})
        return evaluator

    async def run(
        self, args: CalculatorArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | CalculatorResult, None]:
        """Evaluate a mathematical expression safely.

        Args:
            args: Arguments containing the expression to evaluate.
            ctx: Optional invoke context.

        Yields:
            CalculatorResult with the expression, numeric result, and formatted string.

        Raises:
            ToolError: If the expression is invalid or contains undefined names.
        """
        evaluator = self._create_evaluator()

        try:
            result = evaluator.eval(args.expression)
        except NameNotDefined as err:
            raise ToolError(f"Undefined name in expression: {err}") from err
        except InvalidExpression as err:
            raise ToolError(f"Invalid expression: {err}") from err
        except (ZeroDivisionError, ValueError, OverflowError) as err:
            raise ToolError(f"Math error: {err}") from err
        except Exception as err:
            raise ToolError(f"Evaluation error: {err}") from err

        try:
            float_result = float(result)
        except (TypeError, ValueError) as err:
            raise ToolError(
                f"Expression did not produce a numeric result: {result}"
            ) from err

        yield CalculatorResult(
            expression=args.expression,
            result=float_result,
            formatted=f"{float_result:.{self.config.precision}g}",
        )
