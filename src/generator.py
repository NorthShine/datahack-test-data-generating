from typing import Dict, Optional, List, get_type_hints

from expression import Expression, ExpressionParser
from handlers import Handler


class FakeDataGenerator:
    def __init__(
            self,
            model,
            where_clause=None,
            foreign_keys=None,
            limit=10,
            lang='en_US',
    ):
        self.model = model
        self.fields = [*get_type_hints(model)]
        self.limit = limit
        self.lang = lang
        self.conditions_per_field: Dict[str, List[Expression]] = {}
        self._parse_where_clause(where_clause)
        self._parse_foreign_keys(foreign_keys)

    def generate_fake_data(self):
        data = []
        for counter in range(1, self.limit + 1):
            item = {}
            for field_name in self.fields:
                handler = Handler(self.lang, self.conditions_per_field)
                handler.handle(item, field_name, counter)
            data.append(item)
        return data

    def _parse_where_clause(self, where_clause: Optional[str]):
        if where_clause is not None:
            expr_parser = ExpressionParser(where_clause)
            for expr in expr_parser.expressions:
                if expr.field not in self.conditions_per_field.keys():
                    self.conditions_per_field[expr.field] = [expr]
                else:
                    self.conditions_per_field[expr.field].extend([expr])

    def _parse_foreign_keys(self, foreign_keys: Optional[List[Dict[str, str]]]):
        pass


if __name__ == '__main__':
    from example import SimpleModel, User
    from pprint import pprint
    # gen = FakeDataGenerator(SimpleModel, limit=1)
    # pprint(gen.generate_fake_data())

    gen2 = FakeDataGenerator(
        User,
        where_clause='user_id >= 10 AND age < 22 AND age > 20',
        limit=3,
    )
    pprint(gen2.generate_fake_data())
