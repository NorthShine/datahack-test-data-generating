import operator


class Expression:
    sql_comparison_operators = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq,
    }

    def __init__(self, cond: str):
        tokens = cond.split()
        self.field = tokens[0]
        self.comparator = self.sql_comparison_operators.get(tokens[1])
        self.other = tokens[2]
