import pytest
from datetime import datetime
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


def test_no_exception_during_basic_generating(ManyColumnsData):
    generator = FakeDataGenerator(ManyColumnsData)
    generator.load()
