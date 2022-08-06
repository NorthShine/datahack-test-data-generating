import random
import datetime

import pandas as pd

from mimesis import Person, Address, Datetime, Text
from mimesis.locales import Locale


class BaseHandler:
    def __init__(self, lang, mask_per_field, range_per_field, data):
        self.lang = lang.upper()
        self.data = data
        self.range_per_field = range_per_field
        self.mask_per_field = mask_per_field

    def handle(self, item, field_name, field_type, counter):
        raise NotImplemented

    def _process_int_range(self, item, field_name, default_item_range=range(0, 1000)):
        if field_name in self.range_per_field.keys():
            item_range = self.range_per_field[field_name]
            item[field_name] = random.randint(item_range[0], item_range[-1])
        else:
            item[field_name] = random.randint(default_item_range[0], default_item_range[-1])

    def _process_text_range(self, item, field_name):
        if field_name in self.range_per_field.keys():
            item[field_name] = random.choice(self.range_per_field[field_name])


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
            text_generator = Text()
            item[field_name] = text_generator.sentence()


class MimesisPersonProviderHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        keywords = (
            'full_name',
            'last_name',
            'first_name',
            'username',
            'email',
            'telephone',
        )
        for keyword in keywords:
            if keyword in field_name:
                person = Person(eval(f'Locale.{self.lang}'))
                try:
                    item[field_name] = eval(f'person.{keyword}(mask=self.mask_per_field.get(field_name))')
                except (TypeError, AttributeError):
                    item[field_name] = eval(f'person.{keyword}()')


class MimesisAddressProviderHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        keywords = (
            'city',
            'address',
            'country',
            'country_code',
            'building_number',
            'street_address',
            'street_name',
        )
        for keyword in keywords:
            if keyword in field_name:
                address = Address(eval(f'Locale.{self.lang}'))
                item[field_name] = eval(f'address.{keyword}()')


class MimesisDatetimeProviderHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        keywords = (
            'century',
            'date',
            'time',
            'datetime',
            'month',
            'timezone',
            'timestamp',
        )
        for keyword in keywords:
            if keyword in field_name:
                date_time = Datetime(eval(f'Locale.{self.lang}'))
                item[field_name] = eval(f'date_time.{keyword}()')


class IntHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if field_type is int:
            self._process_int_range(item, field_name)


class DateTimeHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if field_type in (datetime.datetime, datetime.date):
            if field_name in self.range_per_field.keys():
                start_date = self.range_per_field[field_name][0]
                end_date = self.range_per_field[field_name][-1]
                item[field_name] = random.choice(pd.date_range(start_date, end_date).tolist())

            if field_name in item:
                item[field_name] = item[field_name].strftime('%d/%m/%Y, %H:%M:%S')


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
            self._process_int_range(item, field_name, (1, 100))


class TitleHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if 'title' in field_name:
            text_gen = Text()
            text = text_gen.sentence()
            new_text = []
            for word in text.split():
                new_text.append(word)
                if '.' in word:
                    break
            item[field_name] = ' '.join(new_text)


class TextHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if field_type is str and field_name in self.range_per_field.keys():
            self._process_text_range(item, field_name)
