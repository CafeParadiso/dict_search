from pprint import pprint
from unittest import mock

from pytest import raises as pytest_raises

from src.dict_search.dict_search import DictSearch
from src.dict_search import exceptions
from . import data


def test_index_malformed():
    with pytest_raises(exceptions.ArraySelectorFormatException):
        list(
            DictSearch().dict_search(
                data.read_fixtures(),
                select_dict={"batch": {"products": {"$index": {1}}}},
            )
        )


def test_index_include():
    counter = 0
    for d_point in data.read_fixtures():
        if not len(d_point["batch"]["products"]) >= 6:
            continue
        comparison = d_point["batch"]["products"][6]
        values = list(
            DictSearch().dict_search(d_point, select_dict={"batch": {"products": {"$index": {6: 1}}}})
        )
        if values:
            counter += 1
            assert values[0].get("batch").get("products") == comparison
    assert counter == 6


def test_index_include_nested():
    counter = 0
    for d_point in data.read_fixtures():
        if len(d_point["batch"]["products"]) >= 5:
            comparison = d_point["batch"]["products"][4]["product"]
        values = list(
            DictSearch().dict_search(d_point, select_dict={"batch": {"products": {"$index": {4: {"product": 1}}}}})
        )
        if values:
            counter += 1
            assert values[0].get("batch").get("products").get("product") == comparison
    assert counter == 6


def test_index_include_generator():
    counter = 0
    for d_point in data.read_fixtures():
        values = list(
            DictSearch().dict_search(d_point, select_dict={"port_route": {"$index": {0: 1}}})
        )
        if values:
            counter += 1
            assert values[0] == {'port_route': {'days': mock.ANY, 'port': mock.ANY}}
    assert counter == 8


def test_index_include_nested_generator():
    counter = 0
    for d_point in data.read_fixtures():
        values = list(
            DictSearch().dict_search(d_point, select_dict={"port_route": {"$index": {0: {"days": 1}}}})
        )
        if values:
            counter += 1
            assert values[0] == {'port_route': {'days': mock.ANY}}
    assert counter == 8


def test_index_exclude():
    counter = 0
    for d_point in data.read_fixtures():
        initial_data = d_point.get("batch", {}).get("products", [None])
        initial_keys = d_point.keys()
        values = list(
            DictSearch().dict_search(d_point, select_dict={"batch": {"products": {"$index": {0: 0}}}})
        )
        if values:
            counter += 1
            assert len(values[0]["batch"]["products"]) == len(initial_data) - 1
            assert values[0].keys() == initial_keys
    assert counter == 10


def test_index_exclude_nested():
    counter = 0
    for d_point in data.read_fixtures():
        initial_data = d_point.get("batch", {}).get("products")
        initial_keys = d_point.keys()
        values = list(
            DictSearch().dict_search(d_point, select_dict={"batch": {"products": {"$index": {0: {"product": 0}}}}})
        )
        if values:
            counter += 1
            assert "product" not in list(values[0]["batch"]["products"][0].keys())
            assert len(values[0]["batch"]["products"]) == len(initial_data)
            assert values[0].keys() == initial_keys
    assert counter == 10


def test_index_exclude_generator():
    counter = 0
    for d_point in data.read_fixtures():
        values = list(
            DictSearch().dict_search(d_point, select_dict={"port_route": {"$index": {0: 0}}})
        )
        if values:
            counter += 1
    assert counter == 8


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
    data = [
                {"a": {"b": [{"b": 1, "c": "ok"}, {"b": 0, "c": "damn"}, {"b": 1, "c": "skate"}]}},
                {"a": {"b": [{"b": 2, "c": "ok"}, {"b": 3, "c": "food"}, {"b": 4, "c": "sneeze "}]}},
            ]
    values = list(
        DictSearch().dict_search(
            data,
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
