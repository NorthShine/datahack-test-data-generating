import random
import datetime

import pandas as pd

from mimesis import Person, Address, Datetime, Text
from mimesis.locales import Locale


class BaseHandler:
    def __init__(
            self,
            lang,
            mask_per_field,
            range_per_field,
            maxlength_per_field,
            data,
            limit,
    ):
        self.lang = lang.upper()
        self.limit = limit
        self.data = data
        self.range_per_field = range_per_field
        self.mask_per_field = mask_per_field or {}
        self.maxlength_per_field = maxlength_per_field or {}

        self.choices_per_field = {}

    def handle(self, item, field_name, field_type, counter):
        raise NotImplemented

    def _set_choices_per_field(self, field_name, item_range, item_frequency_distribution):
        self.choices_per_field[field_name] = random.choices(
            population=item_range,
            weights=item_frequency_distribution,
            k=self.limit,
        )

    def _process_int_range(self, item, field_name, default_item_range=range(0, 1000)):
        if field_name in self.range_per_field.keys():
            item_range = self.range_per_field[field_name]['range']
            item_frequency_distribution = self.range_per_field[field_name].get('frequency_distribution')
            if item_frequency_distribution:
                if field_name not in self.choices_per_field:
                    self._set_choices_per_field(field_name, item_range, item_frequency_distribution)
                item[field_name] = self.choices_per_field[field_name].pop(0)
            else:
                item[field_name] = random.randint(item_range[0], item_range[-1])
        else:
            item[field_name] = random.randint(default_item_range[0], default_item_range[-1])

    def _process_text_range(self, item, field_name):
        if field_name in self.range_per_field.keys():
            item_range = self.range_per_field[field_name]['range']
            item_frequency_distribution = self.range_per_field[field_name].get('frequency_distribution')
            if item_frequency_distribution:
                if field_name not in self.choices_per_field:
                    self._set_choices_per_field(field_name, item_range, item_frequency_distribution)
                item[field_name] = self.choices_per_field[field_name].pop(0)
            else:
                item[field_name] = random.choice(item_range)

    def _process_maxlength(self, item, field_name):
        for field in self.maxlength_per_field:
            if field_name == field['field_name']:
                maxlength = field['maxlength']
                allowed_symbols = field.get('allowed_symbols', 'A')
                if field['fixed']:
                    if len(item[field_name]) < maxlength:
                        shift = maxlength - len(item[field_name])
                        item[field_name] += random.choice(allowed_symbols) * shift
                if len(item[field_name]) > maxlength:
                    item[field_name] = item[field_name][:maxlength]

    def _process_mask(self, item, field_name):
        if field_name in self.mask_per_field.keys():
            mask = self.mask_per_field[field_name]
            fixed_symbols_ids = []
            for char_id, char in enumerate(mask):
                if char != '#':
                    fixed_symbols_ids.append({
                        'id': char_id,
                        'symbol': char,
                    })
            for fixed_symbol in fixed_symbols_ids:
                original_type = type(item[field_name])
                new_string = list(str(item[field_name]))
                for char_id, _ in enumerate(str(item[field_name])):
                    if char_id == fixed_symbol['id']:
                        new_string[char_id] = fixed_symbol['symbol']
                new_string = ''.join(new_string)
                if original_type is not str:
                    new_string = original_type(new_string)
                item[field_name] = new_string


class Handler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        for handler_cls in BaseHandler.__subclasses__():
            if handler_cls is not self.__class__:
                handler = handler_cls(
                    self.lang,
                    self.mask_per_field,
                    self.range_per_field,
                    self.maxlength_per_field,
                    self.data,
                    self.limit,
                )
                handler.handle(item, field_name, field_type, counter)
        if field_name not in item:
            text_generator = Text(eval(f'Locale.{self.lang}'))
            item[field_name] = text_generator.sentence()
            self._process_maxlength(item, field_name)
            self._process_mask(item, field_name)


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
                    item[field_name] = eval(f'person.{keyword}()')
                except (TypeError, AttributeError):
                    item[field_name] = eval(f'person.{keyword}()')
                self._process_maxlength(item, field_name)
                self._process_mask(item, field_name)


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
                self._process_maxlength(item, field_name)
                self._process_mask(item, field_name)


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
        datetime_synonyms = (
            'join_date',
            'created',
            'updated',
            'date_of_birth',
            'joined',
        )
        for keyword in (*keywords, *datetime_synonyms):
            if keyword in field_name:
                date_time = Datetime(eval(f'Locale.{self.lang}'))
                if keyword in datetime_synonyms:
                    item[field_name] = date_time.datetime()
                else:
                    item[field_name] = eval(f'date_time.{keyword}()')


class IntHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if field_type is int:
            self._process_int_range(item, field_name)
            self._process_mask(item, field_name)


class DateTimeHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if field_type in (datetime.datetime, datetime.date, 'datetime', 'date'):
            if field_name in self.range_per_field.keys():
                item_range = self.range_per_field[field_name]['range']
                item_frequency_distribution = self.range_per_field[field_name].get('frequency_distribution')
                if item_frequency_distribution:
                    if field_name not in self.choices_per_field:
                        self._set_choices_per_field(field_name, item_range, item_frequency_distribution)
                    item[field_name] = self.choices_per_field[field_name].pop(0)
                else:
                    start_date = self.range_per_field[field_name]['range'][0]
                    end_date = self.range_per_field[field_name]['range'][-1]
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
                    counter = self.range_per_field[field_name]['range'][0]
                item[field_name] = counter


class AgeHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if 'age' in field_name:
            self._process_int_range(item, field_name, (1, 100))
            self._process_mask(item, field_name)


class TitleHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if 'title' in field_name:
            text = Text(eval(f'Locale.{self.lang}')).sentence()
            new_text = []
            for word in text.split():
                new_text.append(word)
                if '.' in word:
                    break
            item[field_name] = ' '.join(new_text)
            self._process_maxlength(item, field_name)
            self._process_mask(item, field_name)


class TextHandler(BaseHandler):
    def handle(self, item, field_name, field_type, counter):
        if field_type is str and field_name in self.range_per_field.keys():
            self._process_text_range(item, field_name)
            self._process_maxlength(item, field_name)
            self._process_mask(item, field_name)
