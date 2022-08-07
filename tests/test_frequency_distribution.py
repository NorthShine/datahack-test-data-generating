import pytest
from datetime import datetime, timedelta
from dataclasses import make_dataclass

from no_spark_in_my_home.src.generator import FakeDataGenerator


@pytest.fixture(scope='session')
def SimpleDataclass():
    clazz = make_dataclass('SimpleDataclass', [
        ('email', str),
        ('date', datetime),
        ('my_int', int),
    ])
    return clazz


def test_frequency_distribution(SimpleDataclass):
    date_ranges = [
        datetime.now() + timedelta(days=10),
        datetime.now() + timedelta(days=30),
        datetime.now() - timedelta(days=50),
    ]
    gen = FakeDataGenerator(
        SimpleDataclass,
        range_per_field={
            'email': {
                'range': ['a@gmail.com', 'b@gmail.com', 'c@yandex.ru'],
                'frequency_distribution': [0.2, 0.2, 0.8],
            },
            'date': {
                'range': date_ranges,
                'frequency_distribution': [0.2, 0.2, 0.8],
            },
            'my_int': {
                'range': [10, 50, 30],
                'frequency_distribution': [0.2, 0.2, 0.8],
            },
        },
    )
    items = gen.load(as_dicts=True)
    a, b, c = 0, 0, 0
    for item in items:
        if item['email'] == 'a@gmail.com':
            a += 1
        elif item['email'] == 'b@gmail.com':
            b += 1
        elif item['email'] == 'c@yandex.ru':
            c += 1

    assert c >= a and c >= b

    a, b, c = 0, 0, 0
    for item in items:
        if item['date'] == date_ranges[0]:
            a += 1
        elif item['date'] == date_ranges[1]:
            b += 1
        elif item['date'] == date_ranges[2]:
            c += 1

    assert c >= a and c >= b

    a, b, c = 0, 0, 0
    for item in items:
        if item['my_int'] == 10:
            a += 1
        elif item['my_int'] == 50:
            b += 1
        elif item['my_int'] == 30:
            c += 1

    assert c >= a and c >= b
