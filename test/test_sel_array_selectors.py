import types
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
                select_dict={"batch": {"products": {"$index": 1}}},
            )
        )


def test_index_include():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(DictSearch().dict_search(d_point, select_dict={"batch": {"products": {"$index": {6: 1}}}}))
        if values:
            counter += 1
            assert d_point == original_data
            assert values[0]["batch"]["products"] == d_point["batch"]["products"][6]
    assert counter == 6


def test_index_include_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().dict_search(d_point, select_dict={"batch": {"products": {"$index": {4: {"product": 1}}}}})
        )
        if values:
            counter += 1
            assert d_point == original_data
            assert values[0].get("batch").get("products") == {"product": d_point["batch"]["products"][4]["product"]}
    assert counter == 6


def test_index_include_generator():
    counter = 0
    for i, d_point in enumerate(data.read_fixtures()):
        assert isinstance(d_point["port_route"], types.GeneratorType)
        values = list(DictSearch().dict_search(d_point, select_dict={"port_route": {"$index": {0: 1}}}))
        assert isinstance(d_point["port_route"], list)
        assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
        if values:
            counter += 1
            assert values[0] == {"port_route": d_point["port_route"][0]}
    assert counter == 8


def test_index_include_nested_generator():
    counter = 0
    for i, d_point in enumerate(data.read_fixtures()):
        assert isinstance(d_point["port_route"], types.GeneratorType)
        values = list(DictSearch().dict_search(d_point, select_dict={"port_route": {"$index": {0: {"days": 1}}}}))
        assert isinstance(d_point["port_route"], list)
        assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
        if values:
            counter += 1
            assert all(v == {"days": mock.ANY, "port": mock.ANY} for v in d_point["port_route"])
            assert values[0] == {"port_route": {"days": d_point["port_route"][0]["days"]}}
    assert counter == 8


def test_index_exclude():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(DictSearch().dict_search(d_point, select_dict={"batch": {"products": {"$index": {0: 0}}}}))
        if values:
            counter += 1
            assert d_point == original_data
            assert d_point["batch"]["products"][0] not in values[0]["batch"]["products"]
            assert d_point["batch"]["products"][1:] == values[0]["batch"]["products"]
    assert counter == 10


def test_index_exclude_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().dict_search(d_point, select_dict={"batch": {"products": {"$index": {0: {"product": 0}}}}})
        )
        if values:
            counter += 1
            assert d_point == original_data
            assert len(values[0]["batch"]["products"]) == len(original_data["batch"]["products"])
            original_data["batch"]["products"][0].pop("product")
            assert values[0]["batch"]["products"][0] == original_data["batch"]["products"][0]
            assert values[0].keys() == original_data.keys()
    assert counter == 10


def test_index_exclude_generator():
    counter = 0
    for i, d_point in enumerate(data.read_fixtures()):
        assert isinstance(d_point["port_route"], types.GeneratorType)
        values = list(DictSearch().dict_search(d_point, select_dict={"port_route": {"$index": {0: 0}}}))
        assert isinstance(d_point["port_route"], list)
        assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
        if values:
            counter += 1
            assert d_point["port_route"][0] not in values[0]["port_route"]
            assert len(d_point["port_route"]) - 1 == len(values[0]["port_route"])
    assert counter == 8


def test_index_exclude_nested_generator():
    counter = 0
    for i, d_point in enumerate(data.read_fixtures()):
        assert isinstance(d_point["port_route"], types.GeneratorType)
        values = list(DictSearch().dict_search(d_point, select_dict={"port_route": {"$index": {0: {"port": 0}}}}))
        assert isinstance(d_point["port_route"], list)
        assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
        if values:
            counter += 1
            d_point["port_route"][0].pop("port")
            assert d_point["port_route"][0] == values[0]["port_route"][0]
            assert d_point["port_route"][1:] == values[0]["port_route"][1:]
    assert counter == 8


def test_range_malformed():
    with pytest_raises(exceptions.RangeSelectionOperatorError):
        list(
            DictSearch().dict_search(
                data.read_fixtures(), select_dict={"batch": {"products": {"$range": {complex(2, 3): 0}}}}
            )
        )


def test_range_include():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"batch": {"products": {"$range": {":2": 1}}}},
            )
        )
        if values:
            counter += 1
            assert d_point == original_data
            assert values[0]["batch"]["products"] == d_point["batch"]["products"][:2]
    assert counter == 10


def test_range_include_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().dict_search(
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
            DictSearch().dict_search(
                d_point,
                select_dict={"batch": {"products": {"$range": {"2:": 0}}}},
            )
        )
        if values:
            counter += 1
            assert d_point == original_data
            del d_point["batch"]["products"][:2]
            assert d_point == original_data


def test_range_exclude_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"batch": {"products": {"$range": {"2:": {"product": 0}}}}},
            )
        )
        if values:
            counter += 1
            assert d_point == original_data
            [val.pop("product") for val in d_point["batch"]["products"][2:]]
            assert d_point == original_data


def test_where_included():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"batch": {"products": {"$where": [{"product": "Iron"}, 1]}}},
            )
        )
        if values:
            pprint(values)
            counter += 1
            assert d_point == original_data
            for dp in d_point["batch"]["products"]:
                if dp["product"] != "Iron":
                    del dp
            assert d_point == original_data
    assert counter == 3


def test_where_included_nested():
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().dict_search(
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
    counter = 0
    for d_point in data.read_fixtures():
        original_data = d_point.copy()
        values = list(
            DictSearch().dict_search(
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
