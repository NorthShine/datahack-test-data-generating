from datetime import datetime
from dataclasses import dataclass
from pprint import pprint

from src.generator import FakeDataGenerator


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
    limit=1000,
    mask_per_field={
        'username': 'A#2#######',
    },
    range_per_field={
        'age': range(10, 20),
        'user_id': range(10, 100),
    },
    # config='config.json',
)

if __name__ == '__main__':
    user_data_df = user_gen.load()
    user_data_df.show(n=100)
    user_data_as_dicts = user_gen.load(as_dicts=True)
    pprint(user_data_as_dicts)
