import re

from src.dict_search.dict_search import DictSearch

from . import data


def test_ne():
    values = DictSearch().dict_search(data.data, {"fy": {"$ne": 2014}})
    assert len([val for val in values]) == 6


def test_lt():
    values = DictSearch().dict_search(data.data, {"liab": {"cur": {"$lt": 3000}}})
    values = [val for val in values]
    assert len(values) == 3
    assert all([True if val["liab"]["cur"] < 3000 else False for val in values])


def test_lte():
    values = DictSearch().dict_search(data.data, {"liab": {"cur": {"$lte": 2952}}})
    values = [val for val in values]
    assert len(values) == 3
    assert all([True if val["liab"]["cur"] <= 2952 else False for val in values])


def test_gt():
    values = DictSearch().dict_search(data.data, {"assets": {"non_cur": {"$gt": 4000}}})
    values = [val for val in values]
    assert len(values) == 2
    assert all([True if val["assets"]["non_cur"] > 4000 else False for val in values])


def test_gte():
    values = DictSearch().dict_search(data.data, {"assets": {"non_cur": {"$gte": 4586}}})
    values = [val for val in values]
    assert len(values) == 1
    assert all([True if val["assets"]["non_cur"] >= 4586 else False for val in values])


def test_in():
    values = DictSearch().dict_search(data.data, {"fy": {"$in": [2013, 2014]}})
    values = [val for val in values]
    assert len(values) == 4


def test_nin():
    values = DictSearch().dict_search(data.data, {"fy": {"$nin": [2011]}})
    values = [val for val in values]
    assert len(values) == 5


def test_regex_str():
    values = list(DictSearch().dict_search(data.data, {"name": {"$regex": ".*?sm.*?"}}))
    assert len(values) == 2


def test_regex_pattern():
    values = list(DictSearch().dict_search(data.data, {"name": {"$regex": re.compile(".*?sm.*?")}}))
    assert len(values) == 2


def test_regex_wrong():
    values = list(DictSearch().dict_search(data.data, {"name": {"$regex": 1}}))
    assert not values


def test_expr():
    values = DictSearch().dict_search(data.data, {"liab": {"cur": {"$expr": lambda x: x * 2 == 8518}}})
    values = [val for val in values]
    assert len(values) == 1


def test_inst():
    values = DictSearch().dict_search(data.data, {"special": {"$inst": list}})
    values = [val for val in values]
    assert len(values) == 2
