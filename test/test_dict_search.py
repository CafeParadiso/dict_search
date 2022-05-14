from pprint import pprint

import pytest

from src.dict_search.dict_search import DictSearch
from src.dict_search.dict_search import exceptions
from data import data, complex_data, range_data, gene_data  # TODO import data  (refactoring needed)


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


class TestMatchOperators:
    @staticmethod
    def test_match_malformed_query():
        # match as array operator
        results_aop = DictSearch().dict_search(
            [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}],
            {"a": {"$match": [0, 1, 1]}},
        )
        assert not list(results_aop)

    @staticmethod
    def test_match_malformed_count():
        # match as array operator
        results_aop = DictSearch().dict_search(
            [{"a": {1: "2", 2: "3"}, "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}], {"a": {"$match": {"s": 1}}}
        )
        assert not list(results_aop)

    @staticmethod
    def test_match():
        # match as array operator
        results_aop = DictSearch().dict_search(
            [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}], {"a": {"$match": {"1": 1}}}
        )
        assert len(list(results_aop)) == 1
        # match as high level operator
        results_hop = DictSearch().dict_search(
            [{"a": [0, 1, 1], "b": 1, "c": 1}, {"a": [0, 0, 1], "b": 1, "c": 1}],
            {
                "$match": {
                    "2": [
                        {"b": 1},
                        {"b": {"$expr": lambda x: isinstance(x, str)}},
                        {"b": {"$expr": lambda x: isinstance(x, int)}},
                    ]
                }
            },
        )
        assert len(list(results_hop)) == 2

    @staticmethod
    def test_match_compare():
        values = DictSearch().dict_search([{"a": [1, 0]}, {"a": [0, 0]}], {"a": {"$match": {"1": 1}}})
        values = list(values)
        assert len(values) == 1

    @staticmethod
    def test_matchgt():
        values = DictSearch().dict_search(complex_data, {"posts": {"$matchgt": {"1": {"text": "mdb"}}}})
        values = list(values)
        assert len(values) == 2
        assert [val["id"] for val in values] == [5, 6]

    @staticmethod
    def test_matchgte():
        values = DictSearch().dict_search(complex_data, {"posts": {"$matchgte": {"1": {"text": "mdb"}}}})
        values = list(values)
        assert len(values) == 3
        assert [val["id"] for val in values] == [5, 6, 7]

    @staticmethod
    def test_matchlt():
        values = DictSearch().dict_search(complex_data, {"posts": {"$matchlt": {"1": {"text": "mdb"}}}})
        values = list(values)
        assert len(values) == 5
        assert [val["id"] for val in values] == [0, 1, 2, 3, 4]

    @staticmethod
    def test_matchlte():
        values = DictSearch().dict_search(complex_data, {"posts": {"$matchlte": {"1": {"text": "mdb"}}}})
        values = list(values)
        assert len(values) == 6
        assert [val["id"] for val in values] == [0, 1, 2, 3, 4, 7]

    @staticmethod
    def test_match_implicit_and():
        expected_values = 2
        expected_ids = [5, 6]

        values = DictSearch().dict_search(
            complex_data,
            {
                "$and": [
                    {"posts": {"$matchgte": {"1": {"interacted": {"$all": {"type": "post"}}}}}},
                    {"posts": {"$matchgte": {"1": {"text": "mdb"}}}},
                ]
            },
        )
        values = list(values)
        assert len(values) == expected_values
        assert [x["id"] for x in list(values)] == expected_ids

        implicit_values = DictSearch().dict_search(
            complex_data,
            {"posts": {"$matchgte": {"1": {"interacted": {"$all": {"type": "post"}}, "text": "mdb"}}}},
        )
        implicit_values = list(implicit_values)
        assert values == implicit_values


class TestArraySelectors:  # TODO test with data being a generator
    @staticmethod
    def test_index():
        values = DictSearch().dict_search(
            complex_data,
            {"posts": {"$index": {"0": {"interacted": {"$index": {"-1": {"type": "share"}}}}}}},
        )
        pprint(list(values))

    @staticmethod
    def test_range():
        for range_str, val, assert_val in [
            ("2:", 3, 2),
            ("2::", 3, 2),
            (":2", 2, 1),
            (":2:", 2, 1),
            ("::2", 1, 1),
            ("2:6", 3, 2),
            ("2:4:", 2, 2),
            ("2::2", 1, 3),
            (":4:2", 2, 2),
            ("2:5:2", 1, 3),
        ]:
            print(range_str)
            values = DictSearch().dict_search(
                range_data, {"mixed": {"a": {"$range": {range_str: {"$expr": lambda x: x.count(2) == val}}}}}
            )
            assert len(list(values)) == assert_val

    @staticmethod
    def test_where():
        values = DictSearch().dict_search(
            gene_data()["fitxes"]["gg"]["g"],
            {"c": "Territori", "tt": {"t": {"ff": {"f": {"$where": {"c": "Altitud"}}}}}},
        )
        pprint(list(values))


class TestSelect:
    @staticmethod
    def test_select():
        data = gene_data()["fitxes"]["gg"]["g"]
        data[0]["tt"]["t"]["ff"]["f"][0]["calt"] = {"calt": {"gg": "Superfície"}}
        values = DictSearch().dict_search(
            data,
            {"c": "Territori"},
            #"tt"
            #{"tt": {"t": {"ff": {"f": {"$range": "-3:"}}}}},
            #{"tt": {"t": {"ff": {"f": {"$range": {"-3:": "calt"}}}}}},
            #{"tt": {"t": {"ff": {"f": {"$index": -1}}}}},
            {"tt": {"t": {"ff": "f"}}},
        )
        pprint(list(values))


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
    def test_precondition_iterable_exception():
        with pytest.raises(exceptions.PreconditionDataError):
            values = DictSearch().dict_search(1, {"assets": {"curr": {"a": 0}}})
            list(values)

    @staticmethod
    def test_search_dict_precondition():
        with pytest.raises(exceptions.PreconditionSearchDictError):
            values = DictSearch().dict_search(data, 1)
            list(values)

    @staticmethod
    def test_high_level_operator_exception():
        with pytest.raises(exceptions.HighLevelOperatorIteratorError):
            values = DictSearch().dict_search(data, {"$and": {"assets": {"non_cur": {"$lt": 3922}}}})
            list(values)


class TestAll(
    TestData,
    TestCommon,
    TestLowLevelOperators,
    TestHighLevelOperators,
    TestArrayOperators,
    TestMatchOperators,
    TestArraySelectors,
    TestComplex,
    TestExceptions,
):
    pass
