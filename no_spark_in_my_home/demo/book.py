from dataclasses import dataclass

from src.generator import FakeDataGenerator
from demo.user import User, user_gen


@dataclass
class Book:
    book_id: int
    author_id: int
    title: str


book_gen = FakeDataGenerator(
    Book,
    limit=10,
    foreign_keys=[{
        'self_field': 'author_id',
        'other_field': 'user_id',
        'other_model': User,
        'other_data': user_gen.load(as_dicts=True),
    }],
)


if __name__ == '__main__':
    book_df = book_gen.load()
    book_df.show()
