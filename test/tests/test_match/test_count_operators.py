from src.dict_search.dict_search import DictSearch
from src.dict_search.operators.operators import count_operators as cop

from test.utils import BaseTestOperators
from test.new_fixtures.data import PROD_GR


class TestCount(BaseTestOperators.TestOperator):
    thresh = 1
    op = cop.Count(2)
    true_args = [[1, 0, 1], [True, True, False]]
    false_args = [[0, 1, 0], [False, False, True]]
    sub_doc = {"product": PROD_GR}
    search = DictSearch({"products": {"$count": {thresh: sub_doc}}})
    func = lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) == TestCount.thresh


class TestCountGt(BaseTestOperators.TestOperator):
    thresh = 1
    op = cop.Countgt(1)
    true_args = [[1, 0, 1], [True, True, False]]
    false_args = [[0, 1, 0], [False, False, True]]
    sub_doc = {"product": PROD_GR}
    search = DictSearch({"products": {"$countgt": {thresh: sub_doc}}})
    func = lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) > TestCountGt.thresh


class TestCountGte(BaseTestOperators.TestOperator):
    thresh = 1
    op = cop.Countgte(1)
    true_args = [[1, 0, 1], [True, True, False], [0, 1, 0]]
    false_args = [[False, False, False], [0, 0, 0]]
    sub_doc = {"product": PROD_GR}
    search = DictSearch({"products": {"$countgte": {thresh: sub_doc}}})
    func = lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) >= TestCountGte.thresh


class TestCountLt(BaseTestOperators.TestOperator):
    thresh = 2
    op = cop.Countlt(1)
    true_args = [[False, False, False], [0, 0, 0]]
    false_args = [[True, False, False], [1, 0, 0]]
    sub_doc = {"product": PROD_GR}
    search = DictSearch({"products": {"$countlt": {thresh: sub_doc}}})
    func = lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) < TestCountLt.thresh if x["products"] else False


class TestCountLte(BaseTestOperators.TestOperator):
    thresh = 2
    op = cop.Countlte(1)
    true_args = [[False, False, True], [0, 0, 0], [1, 0, 0]]
    false_args = [[False, True, True], [1, 1, 0]]
    search = DictSearch({"products": {"$countlte": {thresh: {"product": PROD_GR}}}})
    func = lambda x: [y["product"] == PROD_GR for y in x["products"]].count(True) <= TestCountLte.thresh if x["products"] else False
