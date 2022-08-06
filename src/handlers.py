import operator
import random

from faker import Faker
from faker.providers import (
    address,
    date_time,
    phone_number,
)

from comparators import in_


class BaseHandler:
    def __init__(self, lang, conditions_per_field, data):
        self.lang = lang
        self.data = data
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
                min_val, max_val = None, None
                for condition in conditions:
                    if condition.is_detailed_other_field and not condition.unique:
                        field_value = random.choice([cond.other_detailed for cond in conditions])
                        break

                    if condition.comparator is operator.eq:
                        return condition.other
                    elif condition.comparator is in_:
                        field_value = random.choice(condition.other)
                        break
                    elif condition.comparator is operator.ge:
                        min_val = int(condition.other)
                    elif condition.comparator is operator.gt:
                        min_val = int(condition.other) + 1
                    elif condition.comparator is operator.le:
                        max_val = int(condition.other)
                    elif condition.comparator is operator.lt:
                        max_val = int(condition.other) - 1

                    comparable_obj = int(condition.other) if condition.other.isdigit() else condition.other
                    while not condition.comparator(field_value, comparable_obj):
                        if min_val is not None and max_val is not None:
                            field_value = random.randint(min_val, max_val)
                        elif min_val is not None and field_value < min_val:
                            field_value = min_val + 1
                        elif max_val is not None and field_value > max_val:
                            field_value -= max_val
        return field_value


class Handler(BaseHandler):
    def handle(self, item, field_name, counter):
        for handler_cls in BaseHandler.__subclasses__():
            if handler_cls is not self.__class__:
                handler = handler_cls(self.lang, self.conditions_per_field, self.data)
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
            new_id = self._apply_conditions(field_name, counter)
            if isinstance(new_id, int):
                ids = [new_id]
                for obj in self.data:
                    ids.append(obj[field_name])
                item[field_name] = max(ids) + 1


class AgeHandler(BaseHandler):
    def handle(self, item, field_name, counter):
        if 'age' in field_name:
            item[field_name] = self._apply_conditions(
                field_name,
                random.randint(1, 100),
            )


class TitleHandler(BaseHandler):
    def handle(self, item, field_name, counter):
        if 'title' in field_name:
            text = self._apply_conditions(field_name, self.fake.text())
            new_text = []
            for word in text.split():
                new_text.append(word)
                if '.' in word:
                    break
            item[field_name] = ' '.join(new_text)
