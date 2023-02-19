from unittest import TestCase

from src.dict_search.dict_search import DictSearch
from src.dict_search.operators.operators import count_operators as cop
from src.dict_search.operators import exceptions as exc

from test.utils import BaseTestOperators
from test.new_fixtures.data import PROD_GR


class TestCount(BaseTestOperators.OperatorMixin, BaseTestOperators.SearchMixin):
    thresh = 1
    operator_checks = cop.Count(2), [[1, 0, 1], [True, True, False]], [[0, 1, 0], [False, False, True]]
    sub_doc = {"product": PROD_GR}
    search_checks = DictSearch({"products": {"$count": {thresh: sub_doc}}}), lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) == TestCount.thresh


class TestCountGt(BaseTestOperators.OperatorMixin, BaseTestOperators.SearchMixin):
    thresh = 1
    operator_checks = cop.Countgt(1), [[1, 0, 1], [True, True, False]], [[0, 1, 0], [False, False, True]]
    sub_doc = {"product": PROD_GR}
    search_checks = DictSearch({"products": {"$countgt": {thresh: sub_doc}}}), lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) > TestCountGt.thresh


class TestCountGte(BaseTestOperators.OperatorMixin, BaseTestOperators.SearchMixin):
    thresh = 1
    operator_checks = cop.Countgte(1), [[1, 0, 1], [True, True, False], [0, 1, 0]], [[False, False, False], [0, 0, 0]]
    sub_doc = {"product": PROD_GR}
    search_checks = DictSearch({"products": {"$countgte": {thresh: sub_doc}}}), lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) >= TestCountGte.thresh


class TestCountLt(BaseTestOperators.OperatorMixin, BaseTestOperators.SearchMixin):
    thresh = 2
    operator_checks = cop.Countlt(1), [[False, False, False], [0, 0, 0]], [[True, False, False], [1, 0, 0]]
    sub_doc = {"product": PROD_GR}
    search_checks = DictSearch({"products": {"$countlt": {thresh: sub_doc}}}), lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) < TestCountLt.thresh if x["products"] else False


class TestCountLte(BaseTestOperators.OperatorMixin, BaseTestOperators.SearchMixin):
    thresh = 2
    operator_checks = cop.Countlte(1), [[False, False, True], [0, 0, 0], [1, 0, 0]], [[False, True, True], [1, 1, 0]]
    search_checks = DictSearch({"products": {"$countlte": {thresh: {"product": PROD_GR}}}}), lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) <= TestCountLte.thresh if x["products"] else False


class TestExceptions(TestCase):
    def test_count_type_error(self):
        with self.assertRaises(exc.CountOperatorError):
            DictSearch({"$count": [1]})

    def test_count_tresh_error(self):
        with self.assertRaises(exc.ThreshTypeError):
            DictSearch({"$count": {"1": [2]}})
