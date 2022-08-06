from dataclasses import dataclass


@dataclass
class SimpleModel:
    item_id: int
    name: str


@dataclass
class User:
    user_id: int
    name: str
    age: int


@dataclass
class Book:
    author: int
    title: str


# user_gen = FakeDataGenerator(User, limit=5, where_clause='age > 20')
# user_data = user_gen.generate_fake_data()
# book_gen = FakeDataGenerator(Book, foreign_keys=[{
#     'self_field': 'author_id',
#     'other_field': 'user_id',
#     'other_model': User,
#     'other_data': user_data,
# }], detailed_relations=True)


"""
Expected output for User dataclass:

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

Expected output for Book dataclass:

[
    {
        "author_id": "10",
        "title": "random title",
    },
]
"""
