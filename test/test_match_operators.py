from src.dict_search.dict_search import DictSearch

from . import data


def test_match_malformed_query():
    # match as array operator
    results_aop = DictSearch().dict_search(
        [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}],
        {"a": {"$match": [0, 1, 1]}},
    )
    assert not list(results_aop)


def test_match_malformed_count():
    # match as array operator
    results_aop = DictSearch().dict_search(
        [{"a": {1: "2", 2: "3"}, "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}], {"a": {"$match": {"s": 1}}}
    )
    assert not list(results_aop)


def test_match():
    # match as array operator
    results_aop = (
        DictSearch().dict_search(
            [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}], {"a": {"$match": {"1": 1}}}
        ),
    )
    assert len(list(results_aop)) == 1
    # match as high level operator
    results_hop = DictSearch().dict_search(
        [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": "1", "c": 1}],
        {
            "$match": {
                "2": [
                    {"b": {"$in": [1, "1"]}},
                    {"b": {"$expr": lambda x: isinstance(x, str)}},
                    {"b": {"$expr": lambda x: isinstance(x, int)}},
                ]
            }
        },
    )
    assert len(list(results_hop)) == 2


def test_match_compare():
    values = DictSearch().dict_search([{"a": [1, 0]}, {"a": [0, 0]}], {"a": {"$match": {"1": 1}}})
    values = list(values)
    assert len(values) == 1


def test_matchgt():
    values = DictSearch().dict_search(data.complex_data, {"posts": {"$matchgt": {"1": {"text": "mdb"}}}})
    values = list(values)
    assert len(values) == 2
    assert [val["id"] for val in values] == [5, 6]


def test_matchgte():
    values = DictSearch().dict_search(data.complex_data, {"posts": {"$matchgte": {"1": {"text": "mdb"}}}})
    values = list(values)
    assert len(values) == 3
    assert [val["id"] for val in values] == [5, 6, 7]


def test_matchlt():
    values = DictSearch().dict_search(data.complex_data, {"posts": {"$matchlt": {"1": {"text": "mdb"}}}})
    values = list(values)
    assert len(values) == 5
    assert [val["id"] for val in values] == [0, 1, 2, 3, 4]


def test_matchlte():
    values = DictSearch().dict_search(data.complex_data, {"posts": {"$matchlte": {"1": {"text": "mdb"}}}})
    values = list(values)
    assert len(values) == 6
    assert [val["id"] for val in values] == [0, 1, 2, 3, 4, 7]


def test_match_implicit_and():
    expected_values = 2
    expected_ids = [5, 6]

    values = DictSearch().dict_search(
        data.complex_data,
        {
            "$and": [
                {"posts": {"$matchgte": {"1": {"interacted": {"$all": {"type": "post"}}}}}},
                {"posts": {"$matchgte": {"1": {"text": "mdb"}}}},
            ]
        },
    )
    values = list(values)
    assert len(values) == expected_values
    assert [x["id"] for x in list(values)] == expected_ids

    implicit_values = DictSearch().dict_search(
        data.complex_data,
        {"posts": {"$matchgte": {"1": {"interacted": {"$all": {"type": "post"}}, "text": "mdb"}}}},
    )
    implicit_values = list(implicit_values)
    assert values == implicit_values
