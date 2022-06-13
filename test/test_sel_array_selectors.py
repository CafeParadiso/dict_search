from pprint import pprint

from pytest import raises as pytest_raises

from src.dict_search.dict_search import DictSearch
from src.dict_search import exceptions
from . import data


def test_index_include_error():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$index": {3: {"b": 1}}}}},
        )
    )
    pprint(values)


def test_index_include():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "food"}, {"b": 1, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$index": {0: 1}}}},
        )
    )
    pprint(values)


def test_index_include_nested():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$index": {0: {"b": 1}}}}},
        )
    )
    pprint(values)
    assert values


def test_index_include_generator():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": (v for v in ["a", "b", "c"])}},
                {"a": {"b": (v for v in ["c", "b", "a"])}},
            ],
            select_dict={"a": {"b": {"$index": {0: 1}}}},
        )
    )
    print(values)


def test_index_include_nested_generator():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": (v for v in [{"a": "a", "b": 1}, {"a": "b", "b": 2}])}},
                {"a": {"b": (v for v in [{"a": "b", "b": 2}, {"a": "a", "b": 1}])}},
            ],
            select_dict={"a": {"b": {"$index": {0: {"a": 1}}}}},
        )
    )
    print(values)


def test_index_exclude():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$index": {0: 0}}}},
        )
    )
    assert values


def test_index_exclude_nested():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$index": {0: {"c": 0}}}}},
        )
    )
    pprint(values)


def test_index_exclude_generator():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": (v for v in ["a", "b", "c"])}},
                {"a": {"b": (v for v in ["c", "b", "a"])}},
            ],
            select_dict={"a": {"b": {"$index": {0: 0}}}},
        )
    )
    print(values)


def test_index_exclude_nested_generator():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": (v for v in [{"a": "a", "b": 1}, {"a": "b", "b": 2}])}},
                {"a": {"b": (v for v in [{"a": "b", "b": 2}, {"a": "a", "b": 1}])}},
            ],
            select_dict={"a": {"b": {"$index": {0: {"a": 0}}}}},
        )
    )
    print(values)


def test_range_malformed():
    with pytest_raises(exceptions.RangeSelectionOperatorError):
        values = list(
            DictSearch().dict_search(
                [
                    {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                    {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
                ],
                select_dict={"a": {"b": {"$range": {complex(2, 3): 0}}}},
            )
        )
        pprint(values)


def test_range_include():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$range": {":2": 1}}}},
        )
    )
    pprint(values)


def test_range_include_nested():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$range": {":2": {"c": 1}}}}},
        )
    )
    pprint(values)


def test_range_exclude():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$range": {":2": 0}}}},
        )
    )
    pprint(values)


def test_range_exclude_nested():
    values = list(
        DictSearch().dict_search(
            [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ],
            select_dict={"a": {"b": {"$range": {":2": {"c": 0}}}}},
        )
    )
    pprint(values)


def test_where_included():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            {"batch": {"products": {"$any": {"product": "Cement"}}}},
            select_dict={"batch": {"products": {"$where": [{"product": "Cement"}, 1]}}},
        )
    )
    pprint(values)


def test_where_included_nested():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            {"batch": {"products": {"$any": {"product": "Wooden"}}}},
            select_dict={
                "batch": {"products": {"$where": [{"product": "Wooden"}, {"type": 1, "product": 1}]}},
                "id": 1,
            },
        )
    )
    pprint(values)


def test_where_excluded():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            {"batch": {"products": {"$any": {"product": "Cement"}}}},
            select_dict={
                "batch": {"products": {"$where": [{"product": "Cement"}, 0]}},
            },
        )
    )
    pprint(values)


def test_where_excluded_nested():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            {"batch": {"products": {"$any": {"product": "Cement"}}}},
            select_dict={
                "batch": {"products": {"$where": [{"product": "Cement"}, {"types": 0}]}},
                "info": 0,
            },
        )
    )
    pprint(values)
