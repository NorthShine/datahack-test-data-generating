from typing import Dict, Callable, List, get_type_hints
import random

from faker import Faker


class FakeDataGenerator:
    limit = 10
    lang = 'en'
    sql_operators_keywords = ('AND', 'OR')
    sql_comparison_operators = ('>', '<', '>=', '<=', '=')

    def __init__(self, model):
        self.model = model
        self.fields = [*get_type_hints(model)]

    def generate_fake_data(self):
        self.parse_special_attributes()
        data = []
        fake = Faker()
        for counter in range(1, self.limit + 1):
            item = {}
            for field_name in self.fields:
                if 'name' in field_name:
                    item[field_name] = fake.name()
                elif 'id' in field_name:
                    item[field_name] = counter
                elif 'age' in field_name:
                    item[field_name] = random.randint(1, 100)
                else:
                    item[field_name] = fake.text()
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
        self.lang = lang.lower()

    def _set_limit(self, new_limit: int) -> None:
        print(1)
        self.limit = new_limit

    def _parse_where_clause(self, where_clause: str):
        tokens = where_clause.split()
        for token in tokens:
            if token not in (self.sql_comparison_operators, self.sql_operators_keywords):
                if token not in self.fields:
                    raise AttributeError(f'WHERE CLAUSE ERROR: There is no such field with name "{token}"')
                # todo: generate fake data based on condition

    def _parse_foreign_keys(self, foreign_keys: List[Dict[str, str]]):
        pass


if __name__ == '__main__':
    from example import SimpleModel
    from pprint import pprint
    gen = FakeDataGenerator(SimpleModel)
    pprint(gen.generate_fake_data())
