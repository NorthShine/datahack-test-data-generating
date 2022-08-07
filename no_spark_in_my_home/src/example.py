from datetime import datetime
from dataclasses import dataclass
from pprint import pprint

from generator import FakeDataGenerator


@dataclass
class User:
    user_id: int
    full_name: str
    age: int
    username: str
    email: str
    telephone: str
    join_date: datetime


user_gen = FakeDataGenerator(
        User,
        limit=5,
        mask_per_field={
            'username': 'C_C_d',
        },
        range_per_field={
            'age': range(10, 20),
            'user_id': range(10, 100),
        },
        config='config.json',
    )
# user_data = user_gen.load(where_clause='age > 15')
user_data = user_gen.load()


"""
@dataclass
class Book:
    book_id: int
    author_id: int
    title: str


book_gen = FakeDataGenerator(Book, limit=10, foreign_keys=[{
    'self_field': 'author_id',
    'other_field': 'user_id',
    'other_model': User,
    'other_data': user_gen.load(as_dicts=True),
}])
book_gen.load()
"""
