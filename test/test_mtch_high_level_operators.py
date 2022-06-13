from pytest import raises as pytest_raises

from src.dict_search.dict_search import DictSearch
from src.dict_search import exceptions

from . import data


def test_high_level_operator_exception():
    with pytest_raises(exceptions.HighLevelOperatorIteratorError):
        list(DictSearch().dict_search(data.data, {"$and": {"assets": {"non_cur": {"$lt": 3922}}}}))


def test_malformed_high_level_operator():
    values = DictSearch().dict_search(
        [{"assets": "a"}, {"assets": 2}, {"assets": [1, 32]}], {"$and": [1, {"assets": "a"}], "missing": [1, 2]}
    )
    results = [val for val in values]
    assert len(results) == 0


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


def test_nested_high_operator():
    values = DictSearch().dict_search(
        data.complex_data,
        {
            "$or": [
                {
                    "$and": [
                        {"posts": {"$match": {1: {"interacted": {"$all": {"type": "post"}}}}}},
                        {"posts": {"$matchgte": {1: {"text": "mdb"}}}},
                    ]
                },
                {"$or": [{"user": {"id": 141}}]},
            ]
        },
    )
    values = list(values)

    assert len(values) == 4
    assert [x["id"] for x in values] == [0, 1, 5, 6]


def test_emtpy_search_container():
    for op in [DictSearch().hop_or, DictSearch().hop_and, DictSearch().hop_not]:
        values = list(DictSearch().dict_search([{"a": 1, "b": 0}, {"a": 0, "b": 1}], {op: []}))
        assert not values


def test_high_level_op_empty_data():
    values = list(
        DictSearch().dict_search(
            [{"a": {"b": 1}}, {"a": None}],
            {"a": {"$and": [{"b": {"$inst": int}}, {"b": 0}]}},
        )
    )
    assert not values
