from pytest import raises as pytest_raises

from src.dict_search.dict_search import DictSearch
from src.dict_search.exceptions import MatchOperatorError

from .fixtures import data


def test_match_array_operator():
    results = list(
        DictSearch().__call__(
            [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}], {"a": {"$match": {1: 1}}}
        ),
    )
    assert len(results) == 1


def test_match_high_level_operator():
    results = list(
        DictSearch().__call__(
            [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": "1", "c": 1}],
            {
                "$match": {
                    2: [
                        {"b": {"$in": [1, "1"]}},
                        {"b": {"$expr": lambda x: isinstance(x, str)}},
                        {"b": {"$expr": lambda x: isinstance(x, int)}},
                    ]
                }
            },
        )
    )
    assert len(results) == 2


def test_match_compare():
    results = list(DictSearch().__call__([{"a": [1, 0]}, {"a": [0, 0]}], {"a": {"$match": {1: 1}}}))
    assert len(results) == 1


def test_matchgt():
    results = list(DictSearch().__call__(data.complex_data, {"posts": {"$matchgt": {1: {"text": "mdb"}}}}))
    assert len(results) == 2
    assert [val["id"] for val in results] == [5, 6]


def test_matchgte():
    results = list(DictSearch().__call__(data.complex_data, {"posts": {"$matchgte": {1: {"text": "mdb"}}}}))
    assert len(results) == 3
    assert [val["id"] for val in results] == [5, 6, 7]


def test_matchlt():
    results = list(DictSearch().__call__(data.complex_data, {"posts": {"$matchlt": {1: {"text": "mdb"}}}}))
    assert len(results) == 5
    assert [val["id"] for val in results] == [0, 1, 2, 3, 4]


def test_matchlte():
    results = list(DictSearch().__call__(data.complex_data, {"posts": {"$matchlte": {1: {"text": "mdb"}}}}))
    assert len(results) == 6
    assert [val["id"] for val in results] == [0, 1, 2, 3, 4, 7]


def test_match_implicit_and():
    expected_results = 2
    expected_ids = [5, 6]

    results = list(
        DictSearch().__call__(
            data.complex_data,
            {
                "$and": [
                    {"posts": {"$matchgte": {1: {"interacted": {"$all": {"type": "post"}}}}}},
                    {"posts": {"$matchgte": {1: {"text": "mdb"}}}},
                ]
            },
        )
    )
    assert len(results) == expected_results
    assert [x["id"] for x in results] == expected_ids

    implicit_results = list(
        DictSearch().__call__(
            data.complex_data,
            {"posts": {"$matchgte": {1: {"interacted": {"$all": {"type": "post"}}, "text": "mdb"}}}},
        )
    )
    assert results == implicit_results


def test_match_malformed_query():
    with pytest_raises(MatchOperatorError):
        list(
            DictSearch().__call__(
                [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}],
                {"a": {"$match": [0, 1, 1]}},
            )
        )


def test_match_malformed_count():
    with pytest_raises(MatchOperatorError):
        list(DictSearch().__call__([{"a": {1: "2", 2: "3"}, "b": True}, {"a": []}], {"a": {"$match": {"s": 1}}}))


def test_match_emtpy_operator():
    with pytest_raises(MatchOperatorError):
        list(DictSearch().__call__([{"a": {1: "2", 2: "3"}, "b": True}, {"a": []}], {"a": {"$match": {}}}))


def test_match_count_mistmatch():
    results = list(DictSearch().__call__([{"a": {1: "2", 2: "3"}}, {"a": []}], {"a": {"$match": {2: [{1: "2"}]}}}))
    assert not results


def test_match_empty_data():
    results = list(
        DictSearch().__call__([{"a": {1: "2", 2: "3"}}, {"a": []}, {}], {"a": {"$match": {1: [{1: "2"}]}}})
    )
    assert len(results) == 1
