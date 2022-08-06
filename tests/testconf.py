import pytest

from dataclasses import make_dataclass


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
