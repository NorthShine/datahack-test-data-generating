import random
from dateutil.rrule import rrule
from datetime import datetime

from faker import Faker
from faker.providers import (
    address,
    date_time,
    phone_number,
)


class BaseHandler:
    def __init__(self, lang, mask_per_field, range_per_field, data):
        self.lang = lang
        self.data = data
        self.range_per_field = range_per_field
        self.mask_per_field = mask_per_field
        self.fake = Faker(self.lang)
        self.fake.add_provider(address)
        self.fake.add_provider(date_time)
        self.fake.add_provider(phone_number)

    def handle(self, item, field_name, field_type, counter):
        raise NotImplemented

    def _process_range(self, item, field_name, default_item_range=range(0, 1000)):
        if field_name in self.range_per_field.keys():
            item_range = self.range_per_field[field_name]
            item[field_name] = random.randint(item_range[0], item_range[-1])
        else:
            item[field_name] = random.randint(default_item_range[0], default_item_range[-1])


class Handler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        for handler_cls in BaseHandler.__subclasses__():
            if handler_cls is not self.__class__:
                handler = handler_cls(
                    self.lang,
                    self.mask_per_field,
                    self.range_per_field,
                    self.data,
                )
                handler.handle(item, field_name, field_type, counter)
        if field_name not in item:
            item[field_name] = self.fake.text()


class IntHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if field_type is int:
            self._process_range(item, field_name)


class FakerProvidersHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
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
                item[field_name] = eval(f'self.fake.{keyword}()')
                # item[field_name] = eval(f'self._apply_conditions("{field_name}", self.fake.{keyword}())')


class IDHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if 'id' in field_name:
            if self.data:
                ids = []
                for obj in self.data:
                    ids.append(obj[field_name])
                item[field_name] = max(ids) + 1
            else:
                if field_name in self.range_per_field.keys():
                    counter = self.range_per_field[field_name][0]
                item[field_name] = counter


class AgeHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if 'age' in field_name:
            self._process_range(item, field_name, (1, 100))


class TitleHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if 'title' in field_name:
            text = self.fake.text()
            new_text = []
            for word in text.split():
                new_text.append(word)
                if '.' in word:
                    break
            item[field_name] = ' '.join(new_text)
