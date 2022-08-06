import json
import operator
from typing import Any, Dict, Optional, List, get_type_hints

from pyspark.sql import SparkSession

from handlers import Handler


class FakeDataGenerator:
    def __init__(
            self,
            model,
            mask_per_field=None,
            range_per_field=None,
            foreign_keys=None,
            limit=10,
            lang='en_US',
            detailed_relations=False,
    ):
        self.model = model
        self.mask_per_field = mask_per_field
        self.range_per_field = range_per_field
        self.detailed_relations = detailed_relations
        self.fields = get_type_hints(model)
        self.limit = limit
        self.lang = lang
        self._parse_foreign_keys(foreign_keys)
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
        return data

    def _save_to_json(self, data):
        with open(self.json_filename, 'a+') as json_file:
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
                self._check_self_field_exists(self_field)
                self._check_other_field_exists(other_field, other_data, other_model)

    def _check_self_field_exists(self, self_field):
        if self_field not in self.fields.keys():
            raise AttributeError(f'There is not such field {self_field} in {self.model.__name__}')

    @staticmethod
    def _check_other_field_exists(other_field, other_data, other_model):
        for item in other_data:
            if other_field not in item.keys():
                raise AttributeError(f'There is not such field {other_field} in {other_model.__name__}')


if __name__ == '__main__':
    from example import SimpleModel, User, Book
    from pprint import pprint
    # simple_gen = FakeDataGenerator(SimpleModel, limit=10)
    # pprint(simple_gen.load_dataclass())

    user_gen = FakeDataGenerator(
        User,
        limit=10,
        range_per_field={'age': range(1, 5), 'user_id': range(10, 100)},
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
        detailed_relations=False,
    )

    pprint(user_data)
    pprint(book_gen.load_dataclass())
"""
