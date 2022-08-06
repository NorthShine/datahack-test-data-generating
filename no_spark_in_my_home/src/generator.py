import json

from random import choice, randint
from collections import deque

from typing import Any, Dict, Optional, List, get_type_hints

from pyspark.sql import SparkSession

from no_spark_in_my_home.src.handlers import Handler


class FakeDataGenerator:
    def __init__(
            self,
            model,
            mask_per_field=None,
            range_per_field=None,
            foreign_keys=None,
            limit=10,
            lang='en_US',
    ):
        self.model = model
        self.mask_per_field = mask_per_field
        self.range_per_field = range_per_field or {}
        self.fields = get_type_hints(model)
        self.limit = limit
        self.lang = lang
        self._parse_foreign_keys(foreign_keys)
        self.foreign_keys = foreign_keys or {}
        self.spark = SparkSession.builder.appName('data-hack-lib').getOrCreate()
        self.json_filename = 'data.json'

    def load(self, as_json=False, where_clause=None):
        data = []
        for counter in range(1, self.limit + 1):
            item = {}
            for field_name, field_type in self.fields.items():
                handler = Handler(
                    self.lang,
                    self.mask_per_field,
                    self.range_per_field,
                    data,
                )
                handler.handle(item, field_name, field_type, counter)
            data.append(item)

        if as_json:
            return json.dumps(data)
        self._save_to_json(json.dumps(data))
        self._parse_where_clause(where_clause)
        self._handle_foreign_key_relations(data)
        return data

    def _save_to_json(self, data):
        with open(self.json_filename, 'w+') as json_file:
            json_file.write(data)

    def _parse_where_clause(self, where_clause: Optional[str]):
        if where_clause is not None:
            json_file = self.spark.read.json(self.json_filename)
            json_file.where(where_clause).show()

    def _parse_foreign_keys(self, foreign_keys: Optional[List[Dict[str, Any]]]):
        if foreign_keys is not None:
            for foreign_key in foreign_keys:
                self_field = foreign_key['self_field']
                other_field = foreign_key['other_field']
                other_data = foreign_key['other_data']
                other_model = foreign_key['other_model']

                self_field = f'{other_model.__name__}_{self_field}'
                self._check_self_field_exists(self_field)
                self._check_other_field_exists(other_field, other_data, other_model)

    @staticmethod
    def _check_other_field_exists(other_field, other_data, other_model):
        for item in other_data:
            if other_field not in item.keys():
                raise AttributeError(f'There is not such field {other_field} in {other_model.__name__}')

    def _check_self_field_exists(self, self_field):
        print(self_field)
        print(self.fields.keys())
        if self_field not in self.fields.keys():
            raise AttributeError(f'There is not such field {self_field} in {self.model.__name__}')

    def _handle_single_foreign_key(self, foreign_key_desc: dict, self_data):
        other_model_field_values = []
        other_field = foreign_key_desc['other_field']
        other_data = foreign_key_desc['other_data']
        other_model = foreign_key_desc['other_model']
        other_model = other_model.__name__
        allow_other_has_no_refs = foreign_key_desc.get('allow_other_has_no_refs')

        for row in other_data:
            other_key_value = row[other_field]
            other_model_field_values.append(other_key_value)
        
        if allow_other_has_no_refs:
            for row in self_data:
                key_value = choice(other_model_field_values)
                row[f'{other_model}_{other_field}'] = key_value
        else:
            other_model_field_values = deque(other_model_field_values)
            shift = randint(1, 100)
            other_model_field_values.rotate(shift)
            for idx, row in enumerate(self_data):
                key_value = other_model_field_values[idx]
                row[f'{other_model}_{other_field}'] = key_value

    def _handle_foreign_key_relations(self, self_data):
        for key in self.foreign_keys:
            self._handle_single_foreign_key(key, self_data)


if __name__ == '__main__':
    from example import SimpleModel, User, Book
    from pprint import pprint
    import datetime
    # simple_gen = FakeDataGenerator(SimpleModel, limit=10)
    # pprint(simple_gen.load_dataclass())

    user_gen = FakeDataGenerator(
        User,
        limit=10,
        range_per_field={
            'age': range(1, 5),
            'user_id': range(10, 100),
            # 'name': ['text', 'text 1', 'text2'],
            'date_of_birth': [
                datetime.date(year=2012, month=1, day=1),
                datetime.date(year=2015, month=1, day=1),
            ],
        },
    )
    user_data = user_gen.load(where_clause='user_id >= 10 AND user_id < 15')
    pprint(user_data)
"""
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
    )

    pprint(user_data)
    pprint(book_gen.load_dataclass())
"""
