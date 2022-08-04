from typing import Dict, Callable, List, get_type_hints

from expression import Expression, ExpressionParser
from handlers import Handler


class FakeDataGenerator:
    limit = 10
    lang = 'en_US'
    conditions_per_field: Dict[str, List[Expression]] = {}

    def __init__(self, model):
        self.model = model
        self.fields = [*get_type_hints(model)]

    def generate_fake_data(self):
        self.parse_special_attributes()
        data = []
        for counter in range(1, self.limit + 1):
            item = {}
            for field_name in self.fields:
                handler = Handler(self.lang, self.conditions_per_field)
                handler.handle(item, field_name, counter)
            data.append(item)
        return data

    def parse_special_attributes(self):
        special_attributes: Dict[str, Callable] = {
            '__lang__': self._set_lang,
            '__limit__': self._set_limit,
            '__where_clause__': self._parse_where_clause,
            '__foreign_keys__': self._parse_foreign_keys,
        }

        for attr_name, attr_value in self.model.__dict__.items():
            try:
                (special_attributes.get(attr_name))(attr_value)
            except TypeError:
                pass

    def _set_lang(self, lang: str):
        self.lang = lang

    def _set_limit(self, new_limit: int) -> None:
        self.limit = new_limit

    def _parse_where_clause(self, where_clause: str):
        expr_parser = ExpressionParser(where_clause)
        for expr in expr_parser.expressions:
            if expr.field not in self.conditions_per_field.keys():
                self.conditions_per_field[expr.field] = [expr]
            else:
                self.conditions_per_field[expr.field].extend([expr])

    def _parse_foreign_keys(self, foreign_keys: List[Dict[str, str]]):
        pass


if __name__ == '__main__':
    from example import SimpleModel, User
    from pprint import pprint
    # gen = FakeDataGenerator(SimpleModel)
    # pprint(gen.generate_fake_data())

    gen2 = FakeDataGenerator(User)
    pprint(gen2.generate_fake_data())
