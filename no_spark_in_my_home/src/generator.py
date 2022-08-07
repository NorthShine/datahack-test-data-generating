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
            maxlength_per_field=None,
            foreign_keys=None,
            limit=10,
            lang='en',
            config=None,
    ):
        self.model = model
        self.config = config
        self.mask_per_field = mask_per_field
        self.range_per_field = range_per_field or {}
        self.maxlength_per_field = maxlength_per_field
        self.fields = get_type_hints(model)
        self.limit = limit
        self.lang = lang
        self._parse_foreign_keys(foreign_keys)
        self.foreign_keys = foreign_keys or {}
        self.spark = SparkSession.builder.appName('data-hack-lib').getOrCreate()
        self.json_filename = 'data.json'

        if config is not None:
            self._use_config()

    def load(
            self,
            as_json=False,
            where_clause=None,
            as_dicts=False,
    ):
        data = []
        for counter in range(1, self.limit + 1):
            item = {}
            for field_name, field_type in self.fields.items():
                handler = Handler(
                    self.lang,
                    self.mask_per_field,
                    self.range_per_field,
                    self.maxlength_per_field,
                    data,
                    self.limit,
                )
                handler.handle(item, field_name, field_type, counter)
            data.append(item)
        self._handle_foreign_key_relations(data)
        self._save_to_json(json.dumps(data))
        df = self.spark.read.json(self.json_filename)
        df = self._parse_where_clause(where_clause) or df
        if as_json:
            return json.dumps(data)
        if as_dicts:
            data = []
            for item in df.toJSON().collect():
                data.append(json.loads(item))
            return data
        return df

    def _use_config(self):
        with open(self.config, 'r') as config:
            json_config = json.loads(config.read())
            for model_name, model_values in json_config.items():
                if model_name.lower() == self.model.__name__.lower():
                    self.limit = model_values.get('limit', self.limit)
                    self.range_per_field = model_values.get('range_per_field', self.range_per_field)
                    self.mask_per_field = model_values.get('mask_per_field', self.mask_per_field)
                    self.maxlength_per_field = model_values.get('maxlength_per_field', self.maxlength_per_field)

    def _save_to_json(self, data):
        with open(self.json_filename, 'w') as json_file:
            json_file.write(data)

    def _parse_where_clause(self, where_clause: Optional[str]):
        if where_clause is not None:
            df = self.spark.read.json(self.json_filename)
            df = df.where(where_clause)
            return df

    def _parse_foreign_keys(self, foreign_keys: Optional[List[Dict[str, Any]]]):
        if foreign_keys is not None:
            for foreign_key in foreign_keys:
                self_field = foreign_key['self_field']
                other_field = foreign_key['other_field']
                other_data = foreign_key['other_data']
                other_model = foreign_key['other_model']
                self._check_self_field_exists(self_field)
                self._check_other_field_exists(other_field, other_data, other_model)

    @staticmethod
    def _check_other_field_exists(other_field, other_data, other_model):
        for item in other_data:
            if other_field not in item.keys():
                raise AttributeError(f'There is not such field {other_field} in {other_model.__name__}')

    def _check_self_field_exists(self, self_field):
        if self_field not in self.fields.keys():
            raise AttributeError(f'There is not such field {self_field} in {self.model.__name__} {self.fields.keys()}')

    def _handle_single_foreign_key(self, foreign_key_desc: dict, self_data):
        other_model_field_values = []
        self_field = foreign_key_desc['self_field']
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
                row[self_field] = key_value
        else:
            other_model_field_values = deque(other_model_field_values)
            shift = randint(1, 100)
            other_model_field_values.rotate(shift)
            for idx, row in enumerate(self_data):
                key_value = other_model_field_values[idx]
                row[self_field] = key_value

    def _handle_foreign_key_relations(self, self_data):
        for key in self.foreign_keys:
            self._handle_single_foreign_key(key, self_data)
