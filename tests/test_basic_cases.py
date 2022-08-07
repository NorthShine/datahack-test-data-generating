import pytest
from datetime import datetime, timedelta
from dataclasses import make_dataclass

from no_spark_in_my_home.src.generator import FakeDataGenerator


@pytest.fixture(scope='session')
def ManyColumnsData():
    clazz = make_dataclass('ManyColumnsData',[
        ('email', str),
        ('some_text', str),
        ('city', str),
        ('date', datetime),
        ('my_int', int),
        ('entity_id', int),
        ('book_title', str),
        ('text', str)
    ])
    return clazz


def test_fixed_maxlength_per_field(ManyColumnsData):
    gen = FakeDataGenerator(
        ManyColumnsData,
        maxlength_per_field=[
            {
                'field_name': 'text',
                'fixed': True,
                'maxlength': 10,
            },
        ],
    )
    items = gen.load(as_dicts=True)
    for item in items:
        assert len(item['text']) == 10


def test_non_fixed_maxlength_per_field(ManyColumnsData):
    gen = FakeDataGenerator(
        ManyColumnsData,
        maxlength_per_field=[
            {
                'field_name': 'text',
                'fixed': False,
                'maxlength': 70,
            },
        ],
    )
    items = gen.load(as_dicts=True)
    for item in items:
        assert len(item['text']) <= 70


def test_maxlength_per_field_allowed_symbols(ManyColumnsData):
    gen = FakeDataGenerator(
        ManyColumnsData,
        maxlength_per_field=[
            {
                'field_name': 'text',
                'fixed': True,
                'maxlength': 1000,
                'allowed_symbols': '!',
            },
        ],
    )
    items = gen.load(as_dicts=True)
    for item in items:
        assert len(item['text']) <= 1000
        if len(item['text']) > 999:
            assert '!' in item['text']


def test_mask(ManyColumnsData):
    gen = FakeDataGenerator(
        ManyColumnsData,
        mask_per_field={
            'text': '1#2A',
            'my_int': '1#0',
        },
        range_per_field={
            'my_int': {
                'range': range(100, 200),
            },
        },
    )
    items = gen.load(as_dicts=True)
    for item in items:
        assert item['text'][0] == '1'
        assert item['text'][2] == '2'
        assert item['text'][3] == 'A'
        assert str(item['my_int'])[0] == '1'
        assert str(item['my_int'])[2] == '0'


def test_ranges(ManyColumnsData):
    date_range = [
        datetime.now() - timedelta(days=5),
        datetime.now() + timedelta(days=10),
    ]
    gen = FakeDataGenerator(
        ManyColumnsData,
        limit=10,
        range_per_field={
            'my_int': {
                'range': range(1, 10),
            },
            'book_title': {
                'range': ['title 1', 'title 2'],
            },
        },
    )
    items = gen.load(as_dicts=True)
    for item in items:
        assert 1 <= item['my_int'] < 10
        assert item['book_title'] in ('title 1', 'title 2')


def test_5k_records_generating(ManyColumnsData):
    generator = FakeDataGenerator(ManyColumnsData, limit=5000)
    gen = generator.load()
    gen.show(n=100)


def test_config(ManyColumnsData):
    gen = FakeDataGenerator(
        ManyColumnsData,
        limit=15,
        config='config.json'
    )
    items = gen.load(as_dicts=True)
    assert len(items) == 3
    for item in items:
        assert 1 <= item['my_int'] <= 5
        assert item['book_title'][0] == 'Q'
