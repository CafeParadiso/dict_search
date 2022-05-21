import pytest

from src.dict_search.dict_search import DictSearch
from src.dict_search.dict_search import exceptions
from . import data


def test_search_dict_precondition():
    with pytest.raises(exceptions.PreconditionError):
        values = DictSearch().dict_search(data.data, 1)
        list(values)


def test_high_level_operator_exception():
    with pytest.raises(exceptions.HighLevelOperatorIteratorError):
        values = DictSearch().dict_search(data.data, {"$and": {"assets": {"non_cur": {"$lt": 3922}}}})
        list(values)
