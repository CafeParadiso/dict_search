from src.dict_search.dict_search import DictSearch
from src.dict_search.operators.operators import match_operators as mop
from src.dict_search.operators import exceptions as exc

from unittest import TestCase
from test.utils import BaseTestOperators as Base
from test.new_fixtures.data import COUNTRY_SPAIN, COUNTRY_MORROCCO


class Match(Base.SearchMixin, Base.OperatorMixin):
    thresh = 2
    operator_checks = mop.Match(thresh), [[1, 0, 1], [True, True, False]], [[0, 1, 0], [False, False, True]]

    def setUp(self) -> None:
        self.search_checks = [
            (DictSearch(
                {
                    "info": {
                        "$match": {
                            self.thresh: [
                                {"origin": COUNTRY_SPAIN},
                                {"ship_country": COUNTRY_MORROCCO},
                                {"port_code": {"$cont": "02"}},
                            ]
                        }
                    }
                }
            ), self.check
            )
        ]
        super(Match, self).setUp()
        self.func = self.check

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
        ]
        return v.count(True) == self.thresh


class MatchGt(Base.SearchMixin, Base.OperatorMixin):
    thresh = 2
    operator_checks = mop.Matchgt(thresh), [[1, 0, 1, 1], [True, True, False, True]], [[0, 1, 0], [False, False, True]]

    def setUp(self) -> None:
        self.search_checks = [
            (DictSearch(
        {
            "info": {
                "$matchgt": {
                    self.thresh: [
                        {"origin": COUNTRY_SPAIN},
                        {"ship_country": COUNTRY_MORROCCO},
                        {"port_code": {"$cont": "02"}},
                        {"departure": {"$func": lambda x: x.month == 5}},
                    ]
                }
            }
        }
    ), self.check)
        ]

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
            x["info"]["departure"].month == 5,
        ]
        return v.count(True) > self.thresh


class MatchGte(Base.SearchMixin, Base.OperatorMixin):
    thresh = 2
    operator_checks = mop.Matchgte(thresh), [[1, 0, 1, 1], [True, True, False]], [[0, 1, 0], [False, False, True]]

    def setUp(self) -> None:
        self.search_checks = [
            (DictSearch(
        {
            "info": {
                "$matchgte": {
                    self.thresh: [
                        {"origin": COUNTRY_SPAIN},
                        {"ship_country": COUNTRY_MORROCCO},
                        {"port_code": {"$cont": "02"}},
                        {"departure": {"$func": lambda x: x.month == 5}},
                    ]
                }
            }
        }
    ), self.check)
        ]

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
            x["info"]["departure"].month == 5,
        ]
        return v.count(True) >= self.thresh


class MatchLt(Base.SearchMixin, Base.OperatorMixin):
    thresh = 2
    operator_checks = mop.Matchlt(thresh), [[0, 1, 0], [False, False, True]],  [[1, 0, 1, 1], [True, True, False]]

    def setUp(self) -> None:
        self.search_checks = [
            (DictSearch(
        {
            "info": {
                "$matchlt": {
                    self.thresh: [
                        {"origin": COUNTRY_SPAIN},
                        {"ship_country": COUNTRY_MORROCCO},
                        {"port_code": {"$cont": "02"}},
                        {"departure": {"$func": lambda x: x.month == 5}},
                    ]
                }
            }
        }
    ), self.check)
        ]

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
            x["info"]["departure"].month == 5,
        ]
        return v.count(True) < self.thresh


class MatchLte(Base.SearchMixin, Base.OperatorMixin):
    thresh = 2
    operator_checks = mop.Matchlte(thresh), [[0, 1, 0], [False, True, True]],  [[1, 0, 1, 1], [False, True, True, True]]

    def setUp(self) -> None:
        self.search_checks = [
            (DictSearch(
        {
            "info": {
                "$matchlte": {
                    self.thresh: [
                        {"origin": COUNTRY_SPAIN},
                        {"ship_country": COUNTRY_MORROCCO},
                        {"port_code": {"$cont": "02"}},
                        {"departure": {"$func": lambda x: x.month == 5}},
                    ]
                }
            }
        }
    ), self.check)
        ]

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
            x["info"]["departure"].month == 5,
        ]
        return v.count(True) <= self.thresh


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
