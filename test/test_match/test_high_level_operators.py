from src.dict_search.dict_search import DictSearch
from src.dict_search.operators import exceptions

from test.utils import TestCase


class TestHighLevelOperators(TestCase):
    def test_high_level_operator_exception(self):
        with self.assertRaises(exceptions.HighLevelOperatorIteratorError):
            self.matching_test(match_query={"$and": {"assets": {"non_cur": {"$lt": 3922}}}})
        with self.assertRaises(exceptions.HighLevelOperatorIteratorError):
            self.matching_test(match_query={"$and": []})

    def test_and(self):
        values, other_values = self.matching_test(
            match_query={"info": {"$and": [{"origin": "Indonesia"}, {"iterms": "DAP"}]}}
        )
        assert len(values) == 1
        equivalent_values, other_values = self.matching_test(
            match_query={"$and": [{"info": {"origin": "Indonesia"}}, {"info": {"iterms": "DAP"}}]}
        )
        assert values[0] == equivalent_values[0]

    def test_or(self):
        values, other_values = self.matching_test(
            match_query={"info": {"$or": [{"origin": "USA"}, {"origin": "Italy"}]}}
        )
        assert [v["info"]["origin"] in ["USA", "Italy"] for v in values], other_values

    def test_not(self):
        values, other_values = self.matching_test(match_query={"$not": [{"reviewed": {"$is": False}}]})
        assert all(v["reviewed"] is not False for v in values)
        assert all(v["reviewed"] is False for v in other_values)

    def test_match_type_precondition(self):
        with self.assertRaises(exceptions.MatchOperatorError):
            DictSearch({"$match": [1]})

    def test_match_int_precondition(self):
        with self.assertRaises(exceptions.MatchOperatorError):
            DictSearch({"$match": {"1": 3}})

    def test_match_search_container_precondition(self):
        with self.assertRaises(exceptions.HighLevelOperatorIteratorError):
            DictSearch({"$match": {1: 3}})

    def test_match_mismatch_precondition(self):
        with self.assertRaises(exceptions.MatchOperatorCountMismatch):
            DictSearch({"$match": {3: [1, 3]}})

    def test_match(self):
        self.hop_matching_test(
            {
                "$match": {
                    2: [
                        {"cargo": {"products": {"$inst": list}}},
                        {"info": {"paid": "no"}},
                        {"combustible_usage(L)": {"$lt": 9000}},
                    ]
                }
            },
            lambda x: x == 2,
        )

    def test_matchgt(self):
        self.hop_matching_test(
            {
                "$matchgt": {
                    1: [{"info": {"origin": "Peru"}}, {"info": {"paid": "no"}}, {"combustible_usage(L)": 14134}]
                }
            },
            lambda x: x > 1,
        )

    def test_matchgte(self):
        self.hop_matching_test(
            {
                "$matchgte": {
                    1: [{"info": {"origin": "Peru"}}, {"info": {"paid": "no"}}, {"combustible_usage(L)": 14134}]
                }
            },
            lambda x: x >= 1,
        )

    def test_matchlt(self):
        self.hop_matching_test(
            {
                "$matchlt": {
                    1: [{"info": {"origin": "Peru"}}, {"info": {"paid": "no"}}, {"combustible_usage(L)": 14134}]
                }
            },
            lambda x: x < 1,
        )

    def test_matchlte(self):
        self.hop_matching_test(
            {
                "$matchlte": {
                    1: [{"info": {"origin": "Peru"}}, {"info": {"paid": "no"}}, {"combustible_usage(L)": 14134}]
                }
            },
            lambda x: x <= 1,
        )
