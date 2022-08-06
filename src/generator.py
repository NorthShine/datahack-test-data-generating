import json
import operator
from typing import Any, Dict, Optional, List, get_type_hints

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
            detailed_relations=False,
    ):
        self.model = model
        self.detailed_relations = detailed_relations
        self.fields = [*get_type_hints(model)]
        self.limit = limit
        self.lang = lang
        self.conditions_per_field: Dict[str, List[Expression]] = {}
        self._parse_where_clause(where_clause)
        self._parse_foreign_keys(foreign_keys)

    def generate_fake_data(self, as_json=False):
        data = []
        for counter in range(1, self.limit + 1):
            item = {}
            for field_name in self.fields:
                handler = Handler(self.lang, self.conditions_per_field, data)
                handler.handle(item, field_name, counter)
            data.append(item)
        if as_json:
            return json.dumps(data)
        return data

    def _parse_where_clause(self, where_clause: Optional[str]):
        if where_clause is not None:
            expr_parser = ExpressionParser(where_clause, self.fields)
            for expr in expr_parser.expressions:
                if expr.field not in self.conditions_per_field.keys():
                    self.conditions_per_field[expr.field] = [expr]
                else:
                    self.conditions_per_field[expr.field].extend([expr])

    def _parse_foreign_keys(self, foreign_keys: Optional[List[Dict[str, Any]]]):
        if foreign_keys is not None:
            for foreign_key in foreign_keys:
                self_field = foreign_key['self_field']
                other_field = foreign_key['other_field']
                other_data = foreign_key['other_data']
                other_model = foreign_key['other_model']
                unique = foreign_key.get('unique', False)
                self._check_self_field_exists(self_field)
                self._check_other_field_exists(other_field, other_data, other_model)

                if self_field not in self.conditions_per_field.keys():
                    self.conditions_per_field[self_field] = []

                for field, conds in self.conditions_per_field.items():
                    if field == self_field:
                        for data in other_data:
                            conds.append(
                                Expression(
                                    field=self_field,
                                    comparator=operator.eq,
                                    other=data[other_field],
                                    is_detailed_other_field=self.detailed_relations,
                                    other_detailed=data,
                                    unique=unique,
                                ),
                            )

    def _check_self_field_exists(self, self_field):
        if self_field not in self.fields:
            raise AttributeError(f'There is not such field {self_field} in {self.model.__name__}')

    @staticmethod
    def _check_other_field_exists(other_field, other_data, other_model):
        for item in other_data:
            if other_field not in item.keys():
                raise AttributeError(f'There is not such field {other_field} in {other_model.__name__}')


if __name__ == '__main__':
    from example import SimpleModel, User, Book
    from pprint import pprint
    # gen = FakeDataGenerator(SimpleModel, limit=1)
    # pprint(gen.generate_fake_data())

    user_gen = FakeDataGenerator(
        User,
        where_clause='user_id >= 10 AND user_id < 15',
        limit=3,
    )
    user_data = user_gen.generate_fake_data()

    book_gen = FakeDataGenerator(
        Book,
        limit=10,
        foreign_keys=[
            {
                'self_field': 'author',
                'other_field': 'user_id',
                'other_model': User,
                'other_data': user_data,
                'unique': False,
            },
        ],
        detailed_relations=False,
    )

    pprint(user_data)
    pprint(book_gen.generate_fake_data())
