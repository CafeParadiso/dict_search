from src.dict_search.dict_search import DictSearch

from . import data


def test_and():
    values = DictSearch().dict_search(
        data.data, {"$and": [{"assets": {"non_cur": {"$lt": 3922}}}, {"fy": {"$in": [2011]}}]}
    )
    values = [val for val in values]
    assert len(values) == 1


def test_or():
    values = DictSearch().dict_search(
        data.data, {"$or": [{"liab": {"non_cur": {"a": {"$gt": 10000}}}}, {"assets": {"curr": {"a": 1}}}]}
    )
    values = [val for val in values]
    assert len(values) == 5


def test_not():
    values = DictSearch().dict_search(
        data.data,
        {
            "$not": [
                {"liab": {"non_cur": {"a": {"$gt": 10000}}}},
                {"assets": {"curr": {"a": 1}}},
            ]
        },
    )
    values = [val for val in values]
    assert len(values) == 5
