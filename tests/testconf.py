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
            ('author_id', int)
        ]
    )
    return clazz



@pytest.fixture(scope='session')
def author_data(Author):
    author_gen = FakeDataGenerator(Author, limit=10)
    return author_gen.load()


@pytest.fixture(scope='session')
def book_data(author_data, Author)
    book_gen = FakeDataGenerator(Book, foreign_keys=[{
        'self_field': 'Author_author_id',
        'other_field': 'author_id',
        'other_model': Author,
        'other_data': author_data,
        'allow_other_has_no_refs': True
    }])
    return book_gen.load()


@pytest.fixture(scope='session')
def every_book_points_at_every_author(author_data, Author)
    book_gen = FakeDataGenerator(Book, foreign_keys=[{
        'self_field': 'Author_author_id',
        'other_field': 'author_id',
        'other_model': Author,
        'other_data': author_data,
    }])
    return book_gen.load()

