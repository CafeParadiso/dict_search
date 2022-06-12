from pytest import raises as pytest_raises

from src.dict_search.dict_search import DictSearch
from src.dict_search import exceptions

from .data import data, complex_data


def test_search_dict_precondition():
    with pytest_raises(exceptions.PreconditionError):
        list(DictSearch().dict_search(data, 1))


def test_operator_char():
    operator_str = "!"
    values = DictSearch(operator_str=operator_str).dict_search(
        [
            {
                "$in": 1,
            },
            {
                "$in": 0,
            },
        ],
        {"$in": 1},
    )
    assert len([val for val in values]) == 1


def test_mixed_type_data():
    values = DictSearch().dict_search(
        [{"demo": 1}, "not_a_dict", 123, {"demo": 2}],
        {"demo": {"$gte": 1}},
    )
    assert len(list(values)) == 2


def test_mixed_type_field():
    values = DictSearch().dict_search(data, {"special": False})
    assert len([val for val in values]) == 5


def test_wrong_type_comparison():
    values = DictSearch().dict_search(data, {"fy": {"$lt": "r"}})
    assert len([val for val in values]) == 0


def test_simple_field():
    values = DictSearch().dict_search(data, {"fy": 2011})
    assert len([val for val in values]) == 3


def test_nested_field():
    values = DictSearch().dict_search(data, {"assets": {"curr": {"a": 0}}})
    assert len([val for val in values]) == 5


def test_multiple_fields():
    values = DictSearch().dict_search(
        data, {"assets": {"curr": {"a": 0}, "non_cur": 4586}, "liab": {"non_cur": {"a": 2447}}}
    )
    results = [val for val in values]
    assert results[0]["name"] == "mdb"
    assert len(results) == 1


def test_malformed_high_level_operator():
    values = DictSearch().dict_search(
        [{"assets": "a"}, {"assets": 2}, {"assets": [1, 32]}], {"$and": [1, {"assets": "a"}], "missing": [1, 2]}
    )
    results = [val for val in values]
    assert len(results) == 0


def test_expected_exception():
    import pandas as pd

    values = list(
        DictSearch(eval_exc=ValueError).dict_search({"df": pd.DataFrame()}, {"df": {"$gt": pd.DataFrame()}})
    )
    assert not values


def test_unexpected_exception():
    import pandas as pd

    with pytest_raises(ValueError):
        list(DictSearch().dict_search({"df": pd.DataFrame()}, {"df": {"$gt": pd.DataFrame()}}))


def test_exc_truth_value_false():
    import pandas as pd

    values = list(
        DictSearch(eval_exc=ValueError, exc_truth_value=True).dict_search(
            {"df": pd.DataFrame()}, {"df": {"$gt": pd.DataFrame()}}
        )
    )
    assert values


def test_search_else_branch():
    values = list(DictSearch().dict_search({"a": {1: []}}, {"a": {1: {"b": 2}}}))
    assert not values


def test_nested_high_operator():
    values = DictSearch().dict_search(
        complex_data,
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


def test_array_selector_and_other():
    values = DictSearch().dict_search(
        complex_data,
        {
            "values": {"$all": {"$gt": 0.5}},
            "user": {"id": {"$lt": 100}},
        },
    )
    values = list(values)
    assert len(values) == 2
    assert [val["user"]["id"] for val in values] == [94, 68]
