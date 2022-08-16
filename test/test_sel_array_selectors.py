import types
from collections import abc
from pprint import pprint

from pytest import raises as pytest_raises

from src.dict_search.dict_search import DictSearch
from src.dict_search import exceptions
from .fixtures import data

search = DictSearch()


def test_index_malformed():
    with pytest_raises(exceptions.IndexOperatorError):
        list(
            DictSearch().__call__(
                data.read_fixtures(),
                select_dict={"batch": {"products": {"$index": 1}}},
            )
        )


def test_index_nested_missing_key():
    values = list(
        DictSearch().__call__(
            data.read_fixtures(), select_dict={"batch": {"products": {"$index": {4: {"missing": 1}}}}}
        )
    )
    assert not values


def test_index_include():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(DictSearch().__call__(d_point, select_dict={"batch": {"products": {"$index": {6: 1}}}}))
        if values:
            counter += 1
            assert d_point == original_data
            assert values[0] == {"batch": {"products": d_point["batch"]["products"][6]}}
    assert counter == 6


def test_index_multiple():
    counter = 0
    d = [
        {"b": "demo", "a": ({"b": 2, "c": 1}, 2, {"b": 4}, {"b": 5})},
        {"a": 1},
        {"a": [{"b": 2, "c": 2}, {"b": 3}, {"b": 4}, {"b": 5}]},
        {"a": {"b": 1}, "b": 4},
        {"a": {"b": {1, "b", 3, 4, 5}}},
        {"b": "1234"},
        {"a": "1234", "b": 1}
    ]
    for d_point in d:
        original_data = d_point.copy()
        values = list(
            DictSearch(coerce_list=True).__call__(
                d_point, select_dict={"a": {"$index": [[0, -1], {"b": 1}]}, "b": 1}
            )

            #DictSearch(coerce_list=True).dict_search(d_point, select_dict={"b": 0, "a": {"b": 0}})
        )
        if values:
            pprint(values)


def test_index_include_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(d_point, select_dict={"batch": {"products": {"$index": {4: {"product": 1}}}}})
        )
        if values:
            counter += 1
            assert d_point == original_data
            assert values[0] == {"batch": {"products": {"product": d_point["batch"]["products"][4]["product"]}}}
    assert counter == 6


def test_index_include_generator():
    counter = 0
    for i, d_point in enumerate(data.read_fixtures()):
        assert isinstance(d_point["port_route"], types.GeneratorType)
        values = list(DictSearch(consumable_iterators=abc.Iterator)(d_point, select_dict={"port_route": {"$index": {0: 1}}}))
        assert isinstance(d_point["port_route"], list)  # assert generator has been transformed
        assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])  # same values as original
        if values:
            counter += 1
            assert values[0] == {"port_route": d_point["port_route"][0]}
    assert counter == 8


def test_index_include_nested_generator():
    counter = 0
    for i, d_point in enumerate(data.read_fixtures()):
        assert isinstance(d_point["port_route"], types.GeneratorType)
        values = list(DictSearch(consumable_iterators=abc.Iterator)(d_point, select_dict={"port_route": {"$index": {0: {"days": 1}}}}))
        assert isinstance(d_point["port_route"], list)
        assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
        if values:
            counter += 1
            assert values[0] == {"port_route": {"days": d_point["port_route"][0]["days"]}}
    assert counter == 7


def test_index_exclude():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(DictSearch().__call__(d_point, select_dict={"batch": {"products": {"$index": {0: 0}}}}))
        if values:
            counter += 1
            assert d_point == original_data
            d_point["batch"]["products"].pop(0)
            assert values[0] == d_point
    assert counter == 10


def test_index_exclude_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(d_point, select_dict={"batch": {"products": {"$index": {0: {"product": 0}}}}})
        )
        if values:
            counter += 1
            assert d_point == original_data
            d_point["batch"]["products"][0].pop("product")
            assert values[0] == d_point
    assert counter == 10


def test_index_exclude_generator():
    counter = 0
    for i, d_point in enumerate(data.read_fixtures()):
        assert isinstance(d_point["port_route"], types.GeneratorType)
        values = list(DictSearch(consumable_iterators=abc.Iterator)(d_point, select_dict={"port_route": {"$index": {0: 0}}}))
        assert isinstance(d_point["port_route"], list)
        assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
        if values:
            counter += 1
            d_point["port_route"].pop(0)
            assert values[0] == d_point
    assert counter == 8


def test_index_exclude_nested_generator():
    counter = 0
    for i, d_point in enumerate(data.read_fixtures()):
        assert isinstance(d_point["port_route"], types.GeneratorType)
        values = list(DictSearch(consumable_iterators=abc.Iterator)(d_point, select_dict={"port_route": {"$index": {0: {"port": 0}}}}))
        assert isinstance(d_point["port_route"], list)
        assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
        if values:
            counter += 1
            d_point["port_route"][0].pop("port")
            assert values[0] == d_point
    assert counter == 7


def test_range_malformed():
    with pytest_raises(exceptions.RangeSelectionOperatorError):
        list(
            DictSearch().__call__(
                data.read_fixtures(), select_dict={"batch": {"products": {"$range": {complex(2, 3): 0}}}}
            )
        )


def test_range_include():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": {"products": {"$range": {":2": 1}}}},
            )
        )
        if values:
            counter += 1
            assert d_point == original_data
            assert values[0] == {"batch": {"products": d_point["batch"]["products"][:2]}}
    assert counter == 10


def test_range_include_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": {"products": {"$range": {":2": {"product": 1}}}}},
            )
        )
        if values:
            counter += 1
            assert d_point == original_data
            assert values[0] == {
                "batch": {"products": [{"product": p["product"]} for p in d_point["batch"]["products"][:2]]}
            }
    assert counter == 10


def test_range_exclude():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": {"products": {"$range": {"2:": 0}}}},
            )
        )
        if values:
            counter += 1
            assert d_point == original_data
            del d_point["batch"]["products"][2:]
            assert values[0] == d_point


def test_range_exclude_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": {"products": {"$range": {"2:": {"product": 0}}}}},
            )
        )
        if values:
            counter += 1
            assert d_point == original_data
            [val.pop("product") for val in d_point["batch"]["products"][2:]]
            assert values[0] == d_point


def test_where_malformed():
    with pytest_raises(exceptions.WhereOperatorError):
        list(
            DictSearch().__call__(
                data.read_fixtures(),
                select_dict={"batch": {"products": {"$where": {"product": "Iron"}}}},
            )
        )


def test_where_included():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": {"products": {"$where": [{"product": "Iron"}, 1]}}},
            )
        )
        if values:
            pprint(values)
            counter += 1
            assert d_point == original_data
            assert values[0] == {
                "batch": {"products": [dp for dp in d_point["batch"]["products"] if dp["product"] == "Iron"]}
            }
    assert counter == 3


def test_where_included_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": {"products": {"$where": [{"product": "Iron"}, {"due": 1}]}}},
            )
        )
        if values:
            assert d_point == original_data
            assert values[0] == {
                "batch": {
                    "products": [
                        {"due": dp["due"]}
                        for dp in list(
                            filter(
                                lambda x: True if x.get("due") and x["product"] == "Iron" else False,
                                d_point["batch"]["products"],
                            )
                        )
                    ]
                }
            }
            counter += 1
    assert counter == 1


def test_where_excluded():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(d_point, select_dict={"batch": {"products": {"$where": [{"product": "Iron"}, 0]}}})
        )
        if values:
            counter += 1
            assert d_point == original_data
            d_point["batch"]["products"] = [dp for dp in d_point["batch"]["products"] if dp["product"] != "Iron"]
            assert values[0] == d_point
    assert counter == 3


def test_where_excluded_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": {"products": {"$where": [{"product": "Iron"}, {"due": 0}]}}},
            )
        )
        if values:
            assert d_point == original_data
            d_point["batch"]["products"] = list(
                filter(
                    lambda x: True if x.get("due") and x["product"] == "Iron" else False, d_point["batch"]["products"]
                )
            )
            for dp in d_point["batch"]["products"]:
                dp.pop("due")
            assert values[0] == d_point
            counter += 1
    assert counter == 1


def test_demo():
    d = [
        {"b": {"y": 1}, "c": 2},
        {"b": {"y": 1, "x": 1, "c": {"x": 3}}, "c": 0},
        {"b": {"y": 1, "x": 1, "c": 1}, "c": 0},
        {"b": ({"y": 1, "x": 1}, {"y": 2, "x": 2}), "c": 1},
        {"b": [{"y": 3}, {"y": 4}, {"x": 2, "y": 5}], "c": 3},
    ]
    print("\nOriginal")
    pprint(d)
    values = list(
        DictSearch().__call__(
            d,
            select_dict={"b": {"y": 0}},
        )
    )
    print("\n Values")
    pprint(values)
    print("\n Data")
    pprint(d)
