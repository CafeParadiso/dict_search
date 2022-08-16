import re

from src.dict_search.dict_search import DictSearch
from src.dict_search import low_level_operators as llop

from .fixtures import data
from .utils import TestCase

search = DictSearch()


class LowLevelOperators(TestCase):
    def test_ne(self):
        print("a")
        s = DictSearch(
            low_level_ops_config={
                "ne": {
                    "exc": (SyntaxError, BrokenPipeError),
                    "exc_val": {SyntaxError: True, BrokenPipeError: True},
                    "ignored": int,
                    "allowed": object,
                }
            },
            #low_level_glob_exc_val=True
        )
        d = [{"id": data.CursedDataSyntax()}, {"id": 3}, {"id": "1"}, {"id": data.CursedDataPipe()}]
        values = list(s(d, {"id": {"$ne": 3}}))
        print(values)

    @staticmethod
    def test_lt():
        values = DictSearch().__call__(data.data, {"liab": {"cur": {"$lt": 3000}}})
        values = [val for val in values]
        assert len(values) == 3
        assert all([True if val["liab"]["cur"] < 3000 else False for val in values])



def test_lte():
    values = DictSearch().__call__(data.data, {"liab": {"cur": {"$lte": 2952}}})
    values = [val for val in values]
    assert len(values) == 3
    assert all([True if val["liab"]["cur"] <= 2952 else False for val in values])


def test_gt():
    values = DictSearch().__call__(data.data, {"assets": {"non_cur": {"$gt": 4000}}})
    values = [val for val in values]
    assert len(values) == 2
    assert all([True if val["assets"]["non_cur"] > 4000 else False for val in values])


def test_gte():
    values = DictSearch().__call__(data.data, {"assets": {"non_cur": {"$gte": 4586}}})
    values = [val for val in values]
    assert len(values) == 1
    assert all([True if val["assets"]["non_cur"] >= 4586 else False for val in values])


def test_in():
    values = DictSearch().__call__(data.data, {"fy": {"$in": [2013, 2014]}})
    values = [val for val in values]
    assert len(values) == 4


def test_nin():
    values = DictSearch().__call__(data.data, {"fy": {"$nin": [2011]}})
    values = [val for val in values]
    assert len(values) == 5


def test_regex_str():
    values = list(DictSearch().__call__(data.data, {"name": {"$regex": ".*?sm.*?"}}))
    assert len(values) == 2


def test_regex_pattern():
    values = list(DictSearch().__call__(data.data, {"name": {"$regex": re.compile(".*?sm.*?")}}))
    assert len(values) == 2


def test_regex_wrong():
    values = list(DictSearch().__call__(data.data, {"name": {"$regex": 1}}))
    assert not values


def test_expr():
    values = DictSearch().__call__(data.data, {"liab": {"cur": {"$expr": lambda x: x * 2 == 8518}}})
    values = [val for val in values]
    assert len(values) == 1


def test_inst():
    values = DictSearch().__call__(data.data, {"special": {"$inst": list}})
    values = [val for val in values]
    assert len(values) == 2


def test_within():
    d = [
        {"a": 2, "b": 2},
        {"a": 2, "b": {"c": 4}},
        {"a": 2, "b": {"c": 2}},
        {"a": 2, "b": 4},
    ]
    values = list(DictSearch().__call__(d, {"a": {"$comp": ["b"]}}))
    print(values)
    values = list(DictSearch().__call__(d, {"a": {"$comp": ["b", "c"]}}))
    print(values)
    values = list(DictSearch().__call__(d, {"a": {"$comp": [["b"], lambda x, y: x ** 2 == y]}}))
    print(values)
    values = list(DictSearch().__call__(d, {"a": {"$comp": [["b", "c"], lambda x, y: x ** 2 == y]}}))
    print(values)
