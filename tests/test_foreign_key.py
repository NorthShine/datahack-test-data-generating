from collections import Counter


def test_at_least_two_books_point_at_author(book_data):
    book_fks = [row['Author_author_id'] for row in book_data]

    counted_fks = Counter(book_fks)
    most_common = counted_fks.most_common(1)
    assert most_common[0][1] > 1


def test_no_other_has_no_refs(author_data, every_book_points_at_every_author):
    author_ids = {row['author_id'] for row in author_data}
    book_fks = [row['Author_author_id'] for row in every_book_points_at_every_author]

    for idx in book_fks:
        assert idx in author_ids
