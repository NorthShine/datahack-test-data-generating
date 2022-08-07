from collections import Counter

from no_spark_in_my_home.src.generator import FakeDataGenerator


def test_at_least_two_books_point_at_author(book_data):
    book_fks = [row['author_id'] for row in book_data]

    counted_fks = Counter(book_fks)
    most_common = counted_fks.most_common(1)
    assert most_common[0][1] > 1


def test_no_other_has_no_refs(author_data, every_book_points_at_every_author):
    author_ids = {row['author_id'] for row in author_data}
    book_fks = [row['author_id'] for row in every_book_points_at_every_author]

    for idx in book_fks:
        assert idx in author_ids


def test_ensure_data_generator_works_without_fks(Book):
    book_data = FakeDataGenerator(Book, limit=10)
    book_data = book_data.load()
