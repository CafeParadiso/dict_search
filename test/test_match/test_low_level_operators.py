import re

from src.dict_search import DictSearch
from src.dict_search.operators import exceptions
from src.dict_search import constants
from src.dict_search.operators import Operator, HighLevelOperator

from test.utils import TestCase
from pprint import pprint


class TestLowLevelOperators(TestCase):
    def test_eq(self):
        x = "Italy"
        values, other_values = self.matching_test({"info": {"origin": x}})
        assert all(v["info"]["origin"] == x for v in values)
        assert all(v["info"]["origin"] != x for v in other_values)

        s = DictSearch()
        print(s)

    def test_ne(self):
        x = "Italy"
        values, other_values = self.matching_test({"info": {"origin": {"$ne": x}}})
        assert all(v["info"]["origin"] != x for v in values)
        assert all(v["info"]["origin"] == x for v in other_values)

    def test_gt(self):
        x = 10849
        values, other_values = self.matching_test({"combustible_usage(L)": {"$gt": x}})
        assert all(v["combustible_usage(L)"] > x for v in values)
        assert all(v["combustible_usage(L)"] <= x for v in other_values)

    def test_gte(self):
        x = 10849
        values, other_values = self.matching_test({"combustible_usage(L)": {"$gte": x}})
        assert all(v["combustible_usage(L)"] >= x for v in values)
        assert all(v["combustible_usage(L)"] < x for v in other_values)

    def test_lt(self):
        x = 10849
        values, other_values = self.matching_test({"combustible_usage(L)": {"$lt": x}})
        assert all(v["combustible_usage(L)"] < x for v in values)
        assert all(v["combustible_usage(L)"] >= x for v in other_values)

    def test_lte(self):
        x = 10849
        values, other_values = self.matching_test({"combustible_usage(L)": {"$lte": x}})
        assert all(v["combustible_usage(L)"] <= x for v in values)
        assert all(v["combustible_usage(L)"] > x for v in other_values)

    def test_is(self):
        values, other_values = self.matching_test({"reviewed": {"$is": False}})
        assert all(x["reviewed"] is False for x in values)
        assert all(x["reviewed"] is not False or not isinstance(x, bool) for x in values)

    def test_in(self):
        x = ["Albania", "Spain"]
        values, other_values = self.matching_test({"info": {"origin": {"$in": x}}})
        assert all(v["info"]["origin"] in x for v in values)
        assert all(v["info"]["origin"] not in x for v in other_values)

    def test_nin(self):
        x = ["Albania", "Spain"]
        values, other_values = self.matching_test({"info": {"origin": {"$nin": x}}})
        assert all(v["info"]["origin"] not in x for v in values)
        assert all(v["info"]["origin"] in x for v in other_values)

    def test_cont(self):
        x = "l"
        values, other_values = self.matching_test({"info": {"origin": {"$cont": x}}})
        assert all(x in v["info"]["origin"] for v in values)
        assert all(x not in v["info"]["origin"] for v in other_values)

    def test_ncont(self):
        x = "l"
        values, other_values = self.matching_test({"info": {"origin": {"$ncont": x}}})
        assert all(x not in v["info"]["origin"] for v in values)
        assert all(x in v["info"]["origin"] for v in other_values)

    def test_regex(self):
        x = {"yss", "YES", "Y"}
        values, other_values = self.matching_test({"info": {"paid": {"$regex": "[yY][eE3]*s*"}}})
        assert all(v["info"]["paid"] in x for v in values)
        assert all(v["info"]["paid"] not in x for v in other_values)
        values, other_values = self.matching_test({"info": {"paid": {"$regex": re.compile("ye*s*", re.IGNORECASE)}}})
        assert all(v["info"]["paid"] in x for v in values)
        assert all(v["info"]["paid"] not in x for v in other_values)

    def test_expr(self):
        y = 8
        values, other_values = self.matching_test({"info": {"arrival": {"$expr": lambda x: x.month == y}}})
        assert all(v["info"]["arrival"].month == y for v in values)
        assert all(v["info"]["arrival"].month != y for v in other_values)

    def test_inst(self):
        x = int
        values, other_values = self.matching_test({"reviewed": {"$inst": x}})
        assert all(isinstance(v["reviewed"], x) for v in values)
        assert all(not isinstance(v["reviewed"], x) for v in other_values)

    def test_comp(self):
        def comp_func(data, comp):
            return data == comp[-1]["origin"]

        values, other_values = self.matching_test({"info": {"origin": {"$comp": [["cargo", "products"], comp_func]}}})
        assert all(v["info"]["origin"] == v["cargo"]["products"][-1]["origin"] for v in values)
        assert all(v["info"]["origin"] != v["cargo"]["products"][-1]["origin"] for v in other_values)

    def test_comp_missing_key(self):
        def comp_func(data, comp):
            return data == comp[-1]["origin"]

        search = DictSearch(match_query={"info": {"origin": {"$comp": [["cargo", "product"], comp_func]}}})
        results = self.filter_results(search, self.data)
        assert not results


class TestExceptions(TestCase):
    def test_regex_precondition(self):
        with self.assertRaises(exceptions.RegexOperatorException):
            DictSearch({"$regex": 2})

    def test_comp_type_precondition(self):
        with self.assertRaises(exceptions.CompOperatorTypeError):
            DictSearch({"$comp": 2})
        with self.assertRaises(exceptions.CompOperatorTypeError):
            DictSearch({"$comp": [1]})

    def test_comp_non_hashable(self):
        with self.assertRaises(exceptions.CompOperatorFirstArgError):
            DictSearch({"$comp": [{1, 2}, 1]})

    def test_comp_all_not_hashable(self):
        with self.assertRaises(exceptions.CompOperatorFirstArgError):
            DictSearch({"$comp": [[1, {2}], 1]})

    def test_comp_not_function(self):
        with self.assertRaises(exceptions.CompOperatorSecondArgError):
            DictSearch({"$comp": [[1, 2], 1]})

    def test_comp_wrong_return_type(self):
        with self.assertRaises(exceptions.CompOperatorReturnTypeError):

            def comp_func(data, comp):
                return data, comp

            self.matching_test({"info": {"origin": {"$comp": [["cargo", "products"], comp_func]}}})
