from collections import abc
import datetime

from pytest import raises as pytest_raises
import types

from src.dict_search.dict_search import DictSearch
from src.dict_search import exceptions

from .fixtures import data
from pprint import pprint


def test_search_dict_precondition():
    with pytest_raises(exceptions.PreconditionError):
        list(DictSearch().__call__(data.read_fixtures(), 1))


def test_mixed_type_data():
    values = DictSearch().__call__(
        [{"demo": 1}, "not_a_dict", 123, {"demo": 2}],
        {"demo": {"$gte": 1}},
    )
    assert len(list(values)) == 2


def test_operator_char():
    operator_str = "!"
    values = DictSearch(operator_str=operator_str).__call__(
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


def test_unexpected_exception():
    with pytest_raises(Exception):
        list(DictSearch().__call__(data.read_fixtures(), {"info": {"suspicious": True}}))
    with pytest_raises(Exception):
        list(DictSearch().__call__(data.read_fixtures(), {"info": {"suspicious": {"$gt": 1}}}))


def test_expected_exception():
    values = list(DictSearch(low_level_glob_exc=Exception).__call__(data.read_fixtures(), {"info": {"suspicious": True}}))
    assert len(values) == 5


def test_exception_truth_value_true():
    values = list(
        DictSearch(low_level_glob_exc=Exception, low_level_glob_exc_val=True).__call__(
            data.read_fixtures(), {"info": {"suspicious": "error"}}
        )
    )
    assert len(values) == 2
    values = list(
        DictSearch(low_level_glob_exc=Exception, low_level_glob_exc_val=True).__call__(
            data.read_fixtures(), {"info": {"suspicious": {"$gt": 2}}}
        )
    )
    assert len(values) == 2


def test_mixed_type_field():
    values = list(DictSearch().__call__(data.read_fixtures(), {"info": {"container": [150, 150]}}))
    assert len(values) == 2 and [4, 6] == [v["id"] for v in values]


def test_wrong_type_comparison():
    values = list(DictSearch().__call__(data.read_fixtures(), {"shipping_date": 12}))
    assert not values


def test_simple_field():
    values = list(DictSearch().__call__(data.read_fixtures(), {"id": 0}))
    assert len(values) == 1 and values[0]["id"] == 0


def test_nested_field():
    values = list(DictSearch().__call__(data.read_fixtures(), {"info": {"origin": "Spain"}}))
    assert len(values) == 2 and [val["id"] for val in values] == [6, 9]


def test_multiple_fields():
    values = list(
        DictSearch(low_level_glob_exc=Exception).__call__(
            data.read_fixtures(),
            {"info": {"suspicious": True}, "shipping_date": {"$gt": datetime.datetime(2022, 5, 1)}},
        )
    )
    assert len(values) == 3 and [val["id"] for val in values] == [3, 6, 8]


def test_unpack_iterator():
    port = "Jebel Ali"
    values = list(DictSearch(consumable_iterators=abc.Iterator)(
        data.read_fixtures(), {"port_route": {"$any": {"port": port}}})
    )
    assert len(values) == 4 and all(port in [v["port"] for v in val["port_route"]] for val in values)


def test_start_iterator():
    port = "Jebel Ali"
    values = list(
        DictSearch().__call__(
            data.read_fixtures(), {"port_route": {"$any": {"port": port}}}, {"port_route": 1}
        )
    )
    assert len(values) == 4
    for val in values:
        assert port not in list(v["port"] for v in val["port_route"])


def test_literal_iterator():
    values = list(DictSearch().__call__(data.read_fixtures(), {"port_route": {"$inst": types.GeneratorType}}))
    assert len(values) == 10 and all(isinstance(val["port_route"], types.GeneratorType) for val in values)


def test_include_broken():
    d = [
        {"a": 1}, {"b": 3, "c": 44}, {"a": {"abc"}}
    ]
    values = list(DictSearch()(d, select_dict={"a": 1}))
