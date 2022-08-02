from dataclasses import dataclass


@dataclass
class SimpleModel:
    item_id: int
    name: str

    __limit__ = 1


@dataclass
class User:
    user_id: int
    name: str
    age: int

    __limit__ = 3
    __where_clause__ = 'user_id >= 10'


@dataclass
class Book:
    author_id: int
    title: str

    __foreign_keys__ = [{'author_id': 'user.user_id'}]


"""
Expected output:

[
    {
        "user_id": 10,
        "name": "john doe"
        "age": 20,
    },
    {
        "user_id": 11,
        "name": "john doe 2"
        "age": 30,
    },
    {
        "user_id": 12,
        "name": "john doe 3"
        "age": 25,
    }
]
"""