from src.dict_search.dict_search import DictSearch

from . import data


def test_all():
    values = DictSearch().dict_search(data.complex_data, {"values": {"$all": {"$gt": 0.5}}})
    values = list(values)
    assert len(values) == 2


def test_all_eq():
    values = DictSearch().dict_search([{"values": [2, 1, 1]}, {"values": [1, 1, 1]}], {"values": {"$all": 1}})
    values = list(values)
    assert len(values) == 1


def test_any():
    values = DictSearch().dict_search(data.complex_data, {"posts": {"$any": {"text": "tsm"}}})
    values = list(values)
    assert len(values) == 1
    assert values[0]["id"] == 0


def test_any_eq():
    values = DictSearch().dict_search(
        [{"values": [0, 1, 1]}, {"values": [1, 1, 1]}, {"values": [0, 0, 1]}, {"values": [0, 0, 2]}],
        {"values": {"$any": 1}},
    )
    values = list(values)
    assert len(values) == 3
