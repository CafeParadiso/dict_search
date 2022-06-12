from copy import deepcopy

from pprint import pprint
from unittest import mock

from src.dict_search.dict_search import DictSearch
from . import data


def test_incomp_first_incl():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"status": 1, "subjects": 0},
        )
    )
    assert all({"status": mock.ANY} == v for v in values) if values else False


def test_incomp_first_excl():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"status": 0, "subjects": 1},
        )
    )
    assert all({"id": mock.ANY, "subjects": mock.ANY, "info": mock.ANY} == v for v in values) if values else False


def test_include_one():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"status": 1},
        )
    )
    assert all({"status": mock.ANY} == v for v in values) if values else False


def test_multiple_include():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"status": 1, "id": 1},
        )
    )
    assert all({"status": mock.ANY, "id": mock.ANY} == v for v in values) if values else False


def test_nested_include():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"info": {"full_name": {"first": 1}, "w": 1}, "id": 1},
        )
    )
    pprint(values)
    assert (
        all({"info": {"full_name": {"first": mock.ANY}, "w": mock.ANY}, "id": mock.ANY} == v for v in values)
        if values
        else False
    )


def test_exclude_one():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"status": 0},
        )
    )
    assert all({"id": mock.ANY, "subjects": mock.ANY, "info": mock.ANY} == v for v in values) if values else False


def test_multiple_exclude():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"status": 0, "id": 0},
        )
    )
    assert all({"subjects": mock.ANY, "info": mock.ANY} == v for v in values) if values else False


def test_nested_exclude():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"info": {"full_name": {"first": 0}}, "id": 0},
        )
    )
    assert (
        all(
            {
                "subjects": mock.ANY,
                "status": mock.ANY,
                "info": {"full_name": {"last": mock.ANY}, "w": mock.ANY, "h": mock.ANY, "mentions": mock.ANY},
            }
            == v
            for v in values
        )
        if values
        else False
    )


def test_wrong_keys():
    values = list(
        DictSearch().dict_search(
            deepcopy(data.student_data),
            {"subjects": {"$cont": "Chemistry"}},
            {"wrong": {"full_name": {"first": 0}}, "id": 0},
        )
    )
    pprint(values)
    assert (
        all(
            {
                "subjects": mock.ANY,
                "status": mock.ANY,
                "info": {
                    "full_name": {"last": mock.ANY, "first": mock.ANY},
                    "w": mock.ANY,
                    "h": mock.ANY,
                    "mentions": mock.ANY,
                },
            }
            == v
            for v in values
        )
        if values
        else False
    )


def test_select_only():
    values = list(DictSearch().dict_search([{"a": 1, "b": 0}, {"a": 2, "b": 1}], select_dict={"a": 1}))
    assert all(v == {"a": mock.ANY} for v in values)


def test_include_array():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            {"order": {"products": {"$any": {"product": "Cement"}}}},
            select_dict={
                "order": {"products": {"types": {"price": 1}}},
                "id": 1,
            },
        )
    )
    pprint(values)


def test_exclude_array():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            {"order": {"products": {"$any": {"product": "Cement"}}}},
            select_dict={"order": {"products": {"types": 0}}, "info": 0},
        )
    )
    pprint(values)


def test_wrong_key():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            {"order": {"products": {"$any": {"product": "Cement"}}}},
            select_dict={"order": "akak"},
        )
    )
    pprint(values)
