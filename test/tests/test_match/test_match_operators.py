from src.dict_search.dict_search import DictSearch
from src.dict_search.operators.operators import match_operators as mop
from src.dict_search.operators import exceptions as exc

from unittest import TestCase
from test.utils import BaseTestOperators
from test.new_fixtures.data import COUNTRY_SPAIN, COUNTRY_MORROCCO


class Match(BaseTestOperators.TestOperator):
    thresh = 2
    op = mop.Match(thresh)
    true_args = [[1, 0, 1], [True, True, False]]
    false_args = [[0, 1, 0], [False, False, True]]
    search = DictSearch(
        {
            "info": {
                "$match": {
                    thresh: [
                        {"origin": COUNTRY_SPAIN},
                        {"ship_country": COUNTRY_MORROCCO},
                        {"port_code": {"$cont": "02"}},
                    ]
                }
            }
        }
    )

    def setUp(self) -> None:
        super(Match, self).setUp()
        self.func = self.check

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
        ]
        return v.count(True) == self.thresh


class MatchGt(BaseTestOperators.TestOperator):
    thresh = 2
    op = mop.Matchgt(thresh)
    true_args = [[1, 0, 1, 1], [True, True, False, True]]
    false_args = [[0, 1, 0], [False, False, True]]
    search = DictSearch(
        {
            "info": {
                "$matchgt": {
                    thresh: [
                        {"origin": COUNTRY_SPAIN},
                        {"ship_country": COUNTRY_MORROCCO},
                        {"port_code": {"$cont": "02"}},
                        {"departure": {"$func": lambda x: x.month == 5}},
                    ]
                }
            }
        }
    )

    def setUp(self) -> None:
        super(MatchGt, self).setUp()
        self.func = self.check

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
            x["info"]["departure"].month == 5,
        ]
        return v.count(True) > self.thresh


class TestExceptions(TestCase):
    def test_match_type_error(self):
        with self.assertRaises(exc.MatchOperatorError):
            DictSearch({"$match": "1"})

    def test_subquery_error(self):
        with self.assertRaises(exc.HighLevelOperatorIteratorError):
            DictSearch({"$match": {"1": 2}})

    def test_thresh_error(self):
        with self.assertRaises(exc.ThreshTypeError):
            DictSearch({"$match": {"1": [2]}})
