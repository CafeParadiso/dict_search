from pprint import pprint

import pytest

from src.dict_search.dict_search import DictSearch
from src.dict_search.dict_search import exceptions
from .data import data, complex_data, range_data, student_data


class TestData:
    @staticmethod
    def test_data():
        assert len(data) == 8
        all(["assets", "fy", "liab", "name", "special"] == list(d.keys()) for d in data)

    @staticmethod
    def test_complex_data():
        assert len(data) == 8
        assert all(["id", "posts", "user", "values"] == list(d.keys()) for d in complex_data)

    @staticmethod
    def test_range_data():
        assert len(range_data) == 4
        assert all(d["mixed"]["a"] for d in range_data)


class TestCommon:
    @staticmethod
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

    @staticmethod
    def test_mixed_type_data():
        values = DictSearch().dict_search(
            [{"demo": 1}, "not_a_dict", 123, {"demo": 2}],
            {"demo": {"$gte": 1}},
        )
        assert len(list(values)) == 2

    @staticmethod
    def test_mixed_type_field():
        values = DictSearch().dict_search(data, {"special": False})
        assert len([val for val in values]) == 5

    @staticmethod
    def test_wrong_type_comparison():
        values = DictSearch().dict_search(data, {"fy": {"$lt": "r"}})
        assert len([val for val in values]) == 0

    @staticmethod
    def test_simple_field():
        values = DictSearch().dict_search(data, {"fy": 2011})
        assert len([val for val in values]) == 3

    @staticmethod
    def test_nested_field():
        values = DictSearch().dict_search(data, {"assets": {"curr": {"a": 0}}})
        assert len([val for val in values]) == 5

    @staticmethod
    def test_multiple_fields():
        values = DictSearch().dict_search(
            data, {"assets": {"curr": {"a": 0}, "non_cur": 4586}, "liab": {"non_cur": {"a": 2447}}}
        )
        results = [val for val in values]
        assert results[0]["name"] == "mdb"
        assert len(results) == 1

    @staticmethod
    def test_malformed_high_level_operator():
        values = DictSearch().dict_search(
            [{"assets": "a"}, {"assets": 2}, {"assets": [1, 32]}], {"$and": [1, {"assets": "a"}], "missing": [1, 2]}
        )
        results = [val for val in values]
        assert len(results) == 0

    @staticmethod
    def test_wrong_type_value_error():
        import pandas as pd
        values = list(DictSearch().dict_search({"df": pd.DataFrame()}, {"df": {"$gt": pd.DataFrame()}}))
        assert not values
        # values = list(DictSearch().dict_search({"df": [pd.DataFrame()]}, {"df": {"$gt": pd.DataFrame()}}))
        # assert not values
        # values = list(DictSearch().dict_search({"df": [pd.DataFrame()]}, {"df": {"$gt": pd.DataFrame()}}))
        # assert not values

    @staticmethod
    def test_search_else_branch():
        values = list(DictSearch().dict_search({"a": {1: []}}, {"a": {1: {"b": 2}}}))
        assert not values


class TestLowLevelOperators:
    @staticmethod
    def test_ne():
        values = DictSearch().dict_search(data, {"fy": {"$ne": 2014}})
        assert len([val for val in values]) == 6

    @staticmethod
    def test_lt():
        values = DictSearch().dict_search(data, {"liab": {"cur": {"$lt": 3000}}})
        values = [val for val in values]
        assert len(values) == 3
        assert all([True if val["liab"]["cur"] < 3000 else False for val in values])

    @staticmethod
    def test_lte():
        values = DictSearch().dict_search(data, {"liab": {"cur": {"$lte": 2952}}})
        values = [val for val in values]
        assert len(values) == 3
        assert all([True if val["liab"]["cur"] <= 2952 else False for val in values])

    @staticmethod
    def test_gt():
        values = DictSearch().dict_search(data, {"assets": {"non_cur": {"$gt": 4000}}})
        values = [val for val in values]
        assert len(values) == 2
        assert all([True if val["assets"]["non_cur"] > 4000 else False for val in values])

    @staticmethod
    def test_gte():
        values = DictSearch().dict_search(data, {"assets": {"non_cur": {"$gte": 4586}}})
        values = [val for val in values]
        assert len(values) == 1
        assert all([True if val["assets"]["non_cur"] >= 4586 else False for val in values])

    @staticmethod
    def test_in():
        values = DictSearch().dict_search(data, {"fy": {"$in": [2013, 2014]}})
        values = [val for val in values]
        assert len(values) == 4

    @staticmethod
    def test_nin():
        values = DictSearch().dict_search(data, {"fy": {"$nin": [2011]}})
        values = [val for val in values]
        assert len(values) == 5

    @staticmethod
    def test_regex():
        values = DictSearch().dict_search(data, {"name": {"$regex": ".*?sm.*?"}})
        values = [val for val in values]
        assert len(values) == 2

    @staticmethod
    def test_expr():
        values = DictSearch().dict_search(data, {"liab": {"cur": {"$expr": lambda x: x * 2 == 8518}}})
        values = [val for val in values]
        assert len(values) == 1

    @staticmethod
    def test_inst():
        values = DictSearch().dict_search(data, {"special": {"$inst": list}})
        values = [val for val in values]
        assert len(values) == 2


class TestHighLevelOperators:
    @staticmethod
    def test_and():
        values = DictSearch().dict_search(
            data, {"$and": [{"assets": {"non_cur": {"$lt": 3922}}}, {"fy": {"$in": [2011]}}]}
        )
        values = [val for val in values]
        assert len(values) == 1

    @staticmethod
    def test_or():
        values = DictSearch().dict_search(
            data, {"$or": [{"liab": {"non_cur": {"a": {"$gt": 10000}}}}, {"assets": {"curr": {"a": 1}}}]}
        )
        values = [val for val in values]
        assert len(values) == 5

    @staticmethod
    def test_not():
        values = DictSearch().dict_search(
            data,
            {
                "$not": [
                    {"liab": {"non_cur": {"a": {"$gt": 10000}}}},
                    {"assets": {"curr": {"a": 1}}},
                ]
            },
        )
        values = [val for val in values]
        assert len(values) == 5


class TestArrayOperators:
    @staticmethod
    def test_all():
        values = DictSearch().dict_search(complex_data, {"values": {"$all": {"$gt": 0.5}}})
        values = list(values)
        assert len(values) == 2

    @staticmethod
    def test_all_eq():
        values = DictSearch().dict_search([{"values": [2, 1, 1]}, {"values": [1, 1, 1]}], {"values": {"$all": 1}})
        values = list(values)
        assert len(values) == 1

    @staticmethod
    def test_any():
        values = DictSearch().dict_search(complex_data, {"posts": {"$any": {"text": "tsm"}}})
        values = list(values)
        assert len(values) == 1
        assert values[0]["id"] == 0

    @staticmethod
    def test_any_eq():
        values = DictSearch().dict_search(
            [{"values": [0, 1, 1]}, {"values": [1, 1, 1]}, {"values": [0, 0, 1]}, {"values": [0, 0, 2]}],
            {"values": {"$any": 1}},
        )
        values = list(values)
        assert len(values) == 3

class TestComplex:
    @staticmethod
    def test_nested_high_operator():
        values = DictSearch().dict_search(
            complex_data,
            {
                "$or": [
                    {
                        "$and": [
                            {"posts": {"$match": {"1": {"interacted": {"$all": {"type": "post"}}}}}},
                            {"posts": {"$matchgte": {"1": {"text": "mdb"}}}},
                        ]
                    },
                    {"$or": [{"user": {"id": 141}}]},
                ]
            },
        )
        values = list(values)

        assert len(values) == 4
        assert [x["id"] for x in values] == [0, 1, 5, 6]

    def test_array_selector_and_other(self):
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


class TestExceptions:
    @staticmethod
    def test_search_dict_precondition():
        with pytest.raises(exceptions.PreconditionError):
            values = DictSearch().dict_search(data, 1)
            list(values)

    @staticmethod
    def test_high_level_operator_exception():
        with pytest.raises(exceptions.HighLevelOperatorIteratorError):
            values = DictSearch().dict_search(data, {"$and": {"assets": {"non_cur": {"$lt": 3922}}}})
            list(values)
