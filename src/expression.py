import typing
import operator
from dataclasses import dataclass

from comparators import in_, not_in


@dataclass(frozen=True, eq=True)
class Expression:
    field: str
    comparator: typing.Callable
    other: str
    is_detailed_other_field: bool = False
    other_detailed: typing.Optional[dict] = None
    sql_operator_after_expression: typing.Optional[str] = None
    unique: bool = False


class ExpressionParser:
    sql_operators = (' AND ', '  ')
    expressions = []

    def __init__(self, expr: str, model_fields):
        self.sql_comparison_operators = {
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '=': operator.eq,
            '!=': operator.ne,
            ' IN ': in_,
            ' NOT_IN ': not_in,
        }
        self.model_fields = model_fields
        self.original_expression = expr
        self.set_case()
        if not self.is_simple_expression(self.original_expression):
            self.cut_expression(self.original_expression)
        else:
            self.parse_expression(self.original_expression)
            
    def is_simple_expression(self, expr):
        return all([op not in expr for op in self.sql_operators])

    def set_case(self):
        if any([op.lower() in self.original_expression for op in self.sql_operators]):
            self.sql_operators = [op.lower() for op in self.sql_operators]

    def cut_expression(self, expr):
        sql_operator = None
        for op in self.sql_operators:
            if op in expr:
                sql_operator = op
                break
        expressions = expr.split(sql_operator)
        for expression in expressions:
            if self.is_simple_expression(expression):
                self.parse_expression(expression, sql_operator)
            else:
                self.cut_expression(expression)
        # wont work in this case: user_id = 5 AND (age = 5 OR (age > 5 AND age < 10))
    
    def parse_expression(self, expression, sql_operator=None):
        tokens = expression.split()
        self.expressions.append(
            Expression(
                field=tokens[0],
                comparator=self.sql_comparison_operators.get(tokens[1]),
                other=tokens[2],
                sql_operator_after_expression=sql_operator,
            ),
        )
