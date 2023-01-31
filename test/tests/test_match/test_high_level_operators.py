from datetime import datetime
from unittest import TestCase

from src.dict_search.dict_search import DictSearch
from src.dict_search.operators.operators import high_level_operators as hop
from src.dict_search.operators import get_operators
from src.dict_search.operators import exceptions

from test.utils import TestCase, BaseTestOperators
from test.new_fixtures.data import COUNTRY_USA, COUNTRY_SPAIN


class TestExceptions(TestCase):
    def test_iterator_error(self):
        for op in get_operators(hop):
            with self.assertRaises(exceptions.HighLevelOperatorIteratorError):
                DictSearch(match_query={"a": {f"${op.name}": (1, 2)}})


class And(BaseTestOperators.TestOperator):
    op = hop.And()
    search = DictSearch({"info": {"$and": [{"origin": COUNTRY_USA}, {"departure": datetime(2022, 6, 1)}]}})
    func = lambda x: x["info"]["origin"] == COUNTRY_USA and x["info"]["departure"] == datetime(2022, 6, 1)
    true_args = [[1, 1], [True, True]]
    false_args = [[0, 1], [False, False]]

    def test_implicit_and(self):
        results = self.filter_results()
        self.assertEqual(
            results,
            self.filter_results(DictSearch({"info": {"origin": COUNTRY_USA, "departure": datetime(2022, 6, 1)}})),
        )


class Or(BaseTestOperators.TestOperator):
    op = hop.Or()
    search = DictSearch({"info": {"$or": [{"origin": COUNTRY_USA}, {"departure": datetime(2022, 6, 1)}]}})
    func = lambda x: x["info"]["origin"] == COUNTRY_USA or x["info"]["departure"] == datetime(2022, 6, 1)
    true_args = [[1, 0], [1, 1], [0, 1], [True, False], [True, True], [False, True]]
    false_args = [[0, 0], [False, False]]


class Not(BaseTestOperators.TestOperator):
    op = hop.Not()
    search = DictSearch({"info": {"$not": [{"origin": COUNTRY_USA}]}})
    func = lambda x: x["info"]["origin"] != COUNTRY_USA
    true_args = [[0, 1], [1, 0], [True, False], [False, True], [0, 0], [False, False]]
    false_args = [[1, 1], [True, True]]


class NotAny(BaseTestOperators.TestOperator):
    op = hop.NotAny()
    search = DictSearch({"info": {"$not_any": [{"origin": COUNTRY_SPAIN}, {"ship_country": COUNTRY_SPAIN}]}})
    func = lambda x: x["info"]["origin"] != COUNTRY_SPAIN and x["info"]["ship_country"] != COUNTRY_SPAIN
    true_args = [[0, 0], [False, False]]
    false_args = [[1, 0], [1, 1], [0, 1], [True, False], [True, True], [False, True]]

    # def test_match_type_precondition(self):
    #     with self.assertRaises(exceptions.MatchOperatorError):
    #         DictSearch({"$match": [1]})
    #
    # def test_match_int_precondition(self):
    #     with self.assertRaises(exceptions.MatchOperatorError):
    #         DictSearch({"$match": {"1": []}})
    #
    # def test_match_search_container_precondition(self):
    #     with self.assertRaises(exceptions.HighLevelOperatorIteratorError):
    #         DictSearch({"$match": {1: 3}})

    # def test_match_mismatch_precondition(self):
    #     with self.assertRaises(exceptions.MatchOperatorCountMismatch):
    #         DictSearch({"$match": {3: [1, 3]}})

    # def test_match(self):
    #     self.hop_matching_test(
    #         {
    #             "$match": {
    #                 2: [
    #                     {"cargo": {"products": {"$inst": list}}},
    #                     {"info": {"paid": "no"}},
    #                     {"combustible_usage(L)": {"$lt": 9000}},
    #                 ]
    #             }
    #         },
    #         lambda x: x == 2,
    #     )
    #
    # def test_matchgt(self):
    #     self.hop_matching_test(
    #         {
    #             "$matchgt": {
    #                 1: [{"info": {"origin": "Peru"}}, {"info": {"paid": "no"}}, {"combustible_usage(L)": 14134}]
    #             }
    #         },
    #         lambda x: x > 1,
    #     )
    #
    # def test_matchgte(self):
    #     self.hop_matching_test(
    #         {
    #             "$matchgte": {
    #                 1: [{"info": {"origin": "Peru"}}, {"info": {"paid": "no"}}, {"combustible_usage(L)": 14134}]
    #             }
    #         },
    #         lambda x: x >= 1,
    #     )
    #
    # def test_matchlt(self):
    #     self.hop_matching_test(
    #         {
    #             "$matchlt": {
    #                 1: [{"info": {"origin": "Peru"}}, {"info": {"paid": "no"}}, {"combustible_usage(L)": 14134}]
    #             }
    #         },
    #         lambda x: x < 1,
    #     )
    #
    # def test_matchlte(self):
    #     self.hop_matching_test(
    #         {
    #             "$matchlte": {
    #                 1: [{"info": {"origin": "Peru"}}, {"info": {"paid": "no"}}, {"combustible_usage(L)": 14134}]
    #             }
    #         },
    #         lambda x: x <= 1,
    #     )
