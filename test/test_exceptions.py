import pytest

from src.dict_search.dict_search import DictSearch
from src.dict_search.dict_search import exceptions
from . import data


def test_search_dict_precondition():
    with pytest.raises(exceptions.PreconditionError):
        list(DictSearch().dict_search(data.data, 1))


def test_high_level_operator_exception():
    with pytest.raises(exceptions.HighLevelOperatorIteratorError):
        list(DictSearch().dict_search(data.data, {"$and": {"assets": {"non_cur": {"$lt": 3922}}}}))


def test_array_selector_exception():
    with pytest.raises(exceptions.ArraySelectorFormatException):
        list(
            DictSearch().dict_search(
                data.complex_data,
                {"posts": {"$index": 1}},
            )
        )


def test_where():
    with pytest.raises(exceptions.WhereOperatorError):
        list(
            DictSearch().dict_search(
                data.student_data,
                {"info": {"mentions": {"$where": {"a": 1}}}},
            )
        )
