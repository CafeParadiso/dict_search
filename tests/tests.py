import re
from datetime import datetime
from pprint import pprint

import pytest

from src.dict_search.dict_search import DictSearch
from src.dict_search.dict_search import exceptions
from test_data import data, complex_data


class TestData:
    @staticmethod
    def test_data():
        assert len(data) == 8
        expected_data = {
            "assets": {"curr": {"a": 0, "b": 0}, "non_cur": 2545},
            "fy": 2014,
            "liab": {"cur": 2830, "non_cur": {"a": 14914}},
            "name": "estc",
            "special": False,
        }
        assert data[2] == expected_data


class TestCommon:
    @staticmethod
    def test_operator_char():
        operator_str = "!"
        data = [
            {
                "$in": 1,
            },
            {
                "$in": 0,
            },
        ]
        values = DictSearch(operator_str=operator_str).dict_search(data, {"$in": 1})
        assert len([val for val in values]) == 1

    @staticmethod
    def test_multi_type_field():
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
        values = DictSearch().dict_search(data, {"liab": {"cur": {"$expr": (lambda x: x * 2, 8518)}}})
        values = [val for val in values]
        assert len(values) == 1
        values = DictSearch().dict_search(data, {"liab": {"cur": {"$expr": (lambda x: x * 2, {"$lt": 6000})}}})
        values = [val for val in values]
        assert len(values) == 3
        with pytest.raises(TypeError):
            list(DictSearch().dict_search(
                data, {"liab": {"cur": {"$expr": ("2", {"$lt": 6000})}}}
            ))

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
    def test_xor():
        values = DictSearch().dict_search(
            data, {"$xor": [{"liab": {"non_cur": {"a": {"$gt": 10000}}}}, {"assets": {"curr": {"a": 1}}}]}
        )
        values = [val for val in values]
        assert len(values) == 2

    @staticmethod
    def test_not():
        values = DictSearch().dict_search(
            data, {"$not": [{"liab": {"non_cur": {"a": {"$gt": 10000}}}}, {"assets": {"curr": {"a": 1}}}]}
        )
        values = [val for val in values]
        assert len(values) == 5


class TestArrayOperators:
    @staticmethod
    def test_all():
        values = DictSearch().dict_search(
            complex_data,
            {"values": {"$all": {"$gt": 0.5}}}
        )
        values = list(values)
        assert len(values) == 2

    @staticmethod
    def test_any():
        values = DictSearch().dict_search(
            complex_data, {"posts": {"$any": {"text": "tsm"}}}
        )
        values = list(values)
        assert len(values) == 1
        assert values[0]["id"] == 0

    @staticmethod
    def test_match():
        values = DictSearch().dict_search(
            complex_data, {"posts": {"$match": {"1": {"text": "mdb"}}}}
        )
        values = list(values)
        assert len(values) == 3
        assert [val["id"] for val in values] == [5, 6, 7]


class TestArraySelectors:
    @staticmethod
    def test_index():
        values = DictSearch().dict_search(
            complex_data,
            {"posts": {"$index": {"0": {"interacted": {"$last": {"type": "share"}}}}}},
        )
        pprint(list(values))

    @staticmethod
    def test_last():
        values = DictSearch().dict_search(
            complex_data, {"posts": {"$last": {"text": "gld"}}},
        )
        values = list(values)
        assert len(values) == 1
        assert [x["id"] for x in list(values)] == [0]


class TestOperatorExtension:
    @staticmethod
    def test_low_level_operators():
        dict_search = DictSearch()
        try:
            assert len(dict_search.low_level_operators) == len(
                [k for k in TestLowLevelOperators.__dict__.keys() if re.match("test_.*?", k)]
            )
        except AssertionError:
            raise AssertionError(
                "If you added a low level operator you must add a "
                "corresponding test in the class 'TestLowLevelOperators'"
            )

    @staticmethod
    def test_high_level_operators():
        dict_search = DictSearch()
        try:
            assert len(dict_search.high_level_operators) == len(
                [k for k in TestHighLevelOperators.__dict__.keys() if re.match("test_.*?", k)]
            )
        except AssertionError:
            raise AssertionError(
                "If you added a high level operator you must add a "
                "corresponding test in the class 'TestHighLevelOperators'"
            )


class TestComplex:
    @staticmethod
    def test_match_implicit_and():
        expected_values = 2
        expected_ids = [5, 6]

        values = DictSearch().dict_search(
            complex_data,
            {
                "$and": [
                    {"posts": {"$match": {"1": {"interacted": {"$all": {"type": "post"}}}}}},
                    {"posts": {"$match": {"1": {"text": "mdb"}}}},
                ]
            },
        )
        values = list(values)
        assert len(values) == expected_values
        assert [x["id"] for x in list(values)] == expected_ids

        values = DictSearch().dict_search(
            complex_data,
            {"posts": {"$match": {"1": {"interacted": {"$all": {"type": "post"}}, "text": "mdb"}}}},
        )
        values = list(values)
        assert len(values) == expected_values
        assert [x["id"] for x in list(values)] == expected_ids

    @staticmethod
    def test_nested_high_operator():
        values = DictSearch().dict_search(
            complex_data,
            {
                "$or": [
                    {"$and": [
                            {"posts": {"$match": {"1": {"interacted": {"$all": {"type": "post"}}}}}},
                            {"posts": {"$match": {"1": {"text": "mdb"}}}},
                    ]},
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
            }
        )
        values = list(values)
        assert len(values) == 2
        assert [val["user"]["id"] for val in values] == [94, 68]


class TestExceptions:
    @staticmethod
    def test_operator_str_exception():
        with pytest.raises(TypeError, match=r".*?must be.*?"):
            DictSearch(1)

    @staticmethod
    def test_precondition_iterable_exception():
        with pytest.raises(exceptions.PreconditionIterableError, match=r".*?iterable.*?"):
            values = DictSearch().dict_search(1, {"assets": {"curr": {"a": 0}}})
            list(values)

    @staticmethod
    def test_search_dict_precondition():
        with pytest.raises(exceptions.PreconditionSearchDictError, match=r".*?dict.*?"):
            values = DictSearch().dict_search(data, 1)
            list(values)

    @staticmethod
    def test_high_level_operator_exception():
        with pytest.raises(exceptions.HighLevelOperatorListError, match=r".*?operators should.*?"):
            values = DictSearch().dict_search(data, {"$and": {"assets": {"non_cur": {"$lt": 3922}}}})
            list(values)


class TestAll(
    TestData,
    TestCommon,
    TestLowLevelOperators,
    TestHighLevelOperators,
    TestOperatorExtension,
    TestExceptions,
    TestArraySelectors,
    TestArrayOperators,
    TestComplex,
):
    pass
