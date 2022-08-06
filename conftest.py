import pytest

from dataclasses import make_dataclass

from no_spark_in_my_home.src.generator import FakeDataGenerator


@pytest.fixture(scope='session')
def Author():
    clazz = make_dataclass(
        'Author',
        [
            ('author_id', int),
            ('name', str),
        ])
    return clazz


@pytest.fixture(scope='session')
def Book():
    clazz = make_dataclass(
        'Book',
        [
            ('book_id', int),
            ('title', str),
            ('Author_author_id', int)
        ]
    )
    return clazz


@pytest.fixture(scope='session')
def author_data(Author):
    user_data: FakeDataGenerator = FakeDataGenerator(Author, limit=10)
    user_data = user_data.load()
    return user_data


@pytest.fixture(scope='session')
def book_data(Book, author_data):
    book_data = FakeDataGenerator(
        Book,
        limit=10,
        foreign_keys=[
            {
                'self_field': 'author_id',
                'other_field': 'author_id',
                'other_model': Author,
                'other_data': author_data,
                'allow_other_has_no_refs': True
            }
        ]
    )
    book_data = book_data.load()
    return book_data


@pytest.fixture(scope='session')
def every_book_points_at_every_author(Book, author_data):
    book_data = FakeDataGenerator(
        Book,
        limit=10,
        foreign_keys=[
            {
                'self_field': 'author_id',
                'other_field': 'author_id',
                'other_model': Author,
                'other_data': author_data,
            }
        ]
    )
    book_data = book_data.load()
    return book_data
