import operator
import random

from faker import Faker
from faker.providers import (
    address,
    date_time,
    phone_number,
)


class BaseHandler:
    def __init__(self, lang, conditions_per_field):
        self.lang = lang
        self.conditions_per_field = conditions_per_field
        self.fake = Faker(self.lang)
        self.fake.add_provider(address)
        self.fake.add_provider(date_time)
        self.fake.add_provider(phone_number)

    def handle(self, item, field_name, counter):
        raise NotImplemented

    def _apply_conditions(self, field_name, field_value):
        for field, conditions in self.conditions_per_field.items():
            if field == field_name:
                for condition in conditions:
                    min_val, max_val = None, None

                    if condition.comparator is operator.eq:
                        return condition.other
                    elif condition.comparator in (operator.ge, operator.gt):
                        min_val = int(condition.other)
                    elif condition.comparator in (operator.le, operator.lt):
                        max_val = int(condition.other)

                    comparable_obj = int(condition.other) if condition.other.isdigit() else condition.other
                    while not condition.comparator(field_value, comparable_obj):
                        if min_val is not None:
                            field_value += min_val
                        elif max_val is not None:
                            field_value -= max_val
        return field_value


class Handler(BaseHandler):
    def handle(self, item, field_name, counter):
        for handler_cls in BaseHandler.__subclasses__():
            if handler_cls is not self.__class__:
                handler = handler_cls(self.lang, self.conditions_per_field)
                handler.handle(item, field_name, counter)
        if field_name not in item:
            item[field_name] = self._apply_conditions(field_name, self.fake.text())


class FakerProvidersHandler(BaseHandler):
    def handle(self, item, field_name, counter):
        keywords = (
            'name',
            'city',
            'address',
            'country',
            'country_code',
            'building_number',
            'street_address',
            'street_name',
            'century',
            'date',
            'time',
            'date_of_birth',
            'date_time',
            'month',
            'timezone',
            'phone_number',
        )
        for keyword in keywords:
            if keyword in field_name:
                item[field_name] = eval(f'self._apply_conditions("{field_name}", self.fake.{keyword}())')


class IDHandler(BaseHandler):
    def handle(self, item, field_name, counter):
        if 'id' in field_name:
            item[field_name] = self._apply_conditions(field_name, counter)


class AgeHandler(BaseHandler):
    def handle(self, item, field_name, counter):
        if 'age' in field_name:
            item[field_name] = self._apply_conditions(
                field_name,
                random.randint(1, 100),
            )
