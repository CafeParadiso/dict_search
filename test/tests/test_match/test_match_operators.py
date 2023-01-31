from src.dict_search.dict_search import DictSearch
from src.dict_search.operators.operators import match_operators as mop

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


class MatchGte(BaseTestOperators.TestOperator):
    thresh = 2
    op = mop.Matchgte(thresh)
    true_args = [[1, 0, 1], [True, True, False]]
    false_args = [[0, 1, 0], [False, False, True]]
    search = DictSearch(
        {
            "info": {
                "$matchgte": {
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
        super(MatchGte, self).setUp()
        self.func = self.check

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
            x["info"]["departure"].month == 5,
        ]
        return v.count(True) >= self.thresh


class MatchLt(BaseTestOperators.TestOperator):
    thresh = 2
    op = mop.Matchlt(thresh)
    true_args = [[1, 0, 0], [True, False, False]]
    false_args = [[0, 1, 1], [False, True, True]]
    search = DictSearch(
        {
            "info": {
                "$matchlt": {
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
        super(MatchLt, self).setUp()
        self.func = self.check

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
            x["info"]["departure"].month == 5,
        ]
        return v.count(True) < self.thresh


class MatchLte(BaseTestOperators.TestOperator):
    thresh = 2
    op = mop.Matchlte(thresh)
    true_args = [[1, 0, 1], [True, True, False]]
    false_args = [[0, 1, 1, 1], [False, True, True, True]]
    search = DictSearch(
        {
            "info": {
                "$matchlte": {
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
        super(MatchLte, self).setUp()
        self.func = self.check

    def check(self, x):
        v = [
            x["info"]["origin"] == COUNTRY_SPAIN,
            x["info"].get("ship_country") == COUNTRY_MORROCCO,
            "02" in x["info"]["port_code"],
            x["info"]["departure"].month == 5,
        ]
        return v.count(True) <= self.thresh
