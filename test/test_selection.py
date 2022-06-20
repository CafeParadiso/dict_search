from unittest import mock

from src.dict_search.dict_search import DictSearch
from . import data


def test_malformed():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"id": "1"},
        )
    )
    assert not values


def test_mixed_include():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"id": 1, "batch": 0},
        )
    )
    assert len(values) == 10 and all({"id": mock.ANY} == v for v in values)


def test_mixed_exclude():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"id": 0, "batch": 1},
        )
    )
    assert (
        len(values) == 10
        and all("id" not in v.keys() and "batch" in v.keys() for v in values)
        and all(len(v.keys()) > 1 for v in values)
    )


def test_include_missing_key():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"missing": 1},
        )
    )
    assert not values
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"id": 1, "missing": 1},
        )
    )
    assert len(values) == 10 and values == [{"id": i} for i, v in enumerate(values)]


def test_include_one():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"id": 1},
        )
    )
    assert len(values) == 10 and values == [{"id": i} for i, v in enumerate(values)]


def test_include_multiple():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"paid": 1, "id": 1},
        )
    )
    assert len(values) == 10 and all({"id": mock.ANY, "paid": mock.ANY} == v for v in values)


def test_include_nested():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"info": {"origin": 1}, "id": 1},
        )
    )
    assert len(values) == 10 and all({"info": {"origin": mock.ANY}, "id": mock.ANY} == v for v in values)


def test_include_in_list():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={
                "batch": {"products": {"types": {"price": 1}}},
                "id": 1,
            },
        )
    )
    assert len(values) == 10 and all(
        {"batch": {"products": mock.ANY}, "id": i} == val
        or {"id": i} == val
        and all({"price": mock.ANY} == v for va in val["batch"]["products"] for v in va["types"])
        if "batch" in val.keys()
        else True
        for i, val in enumerate(values)
    )


def test_include_in_iterator():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"port_route": {"port": 1}},
        )
    )
    assert len(values) == 8
    assert all({"port": mock.ANY} == v for val in values for v in val["port_route"])


def test_exclude_missing_key():
    values = list(
        DictSearch().dict_search(
            data.read_fixtures(),
            select_dict={"missing": 0},
        )
    )
    assert not values
    for d_point in data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"id": 0, "missing": 0},
            )
        )
        assert values
        keys.remove("id")
        assert list(values[0].keys()) == keys


def test_exclude_one():
    counter = 0
    for d_point in data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"batch": 0},
            )
        )
        assert values
        counter += 1
        keys.remove("batch")
        assert list(values[0].keys()) == keys
    assert counter == 10


def test_exclude_multiple():
    counter = 0
    for d_point in data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"batch": 0, "id": 0},
            )
        )
        assert values
        counter += 1
        [keys.remove(k) for k in ["batch", "id"]]
        assert list(values[0].keys()) == keys
    assert counter == 10


def test_exclude_nested():
    counter = 0
    for d_point in data.read_fixtures():
        keys = list(d_point.keys())
        info_keys = list(d_point["info"].keys())
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"info": {"origin": 0}, "id": 0},
            )
        )
        assert values
        counter += 1
        keys.remove("id")
        assert list(values[0].keys()) == keys
        info_keys.remove("origin")
        assert list(values[0]["info"].keys()) == info_keys
    assert counter == 10


def test_exclude_in_list():
    counter = 0
    for d_point in data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"batch": {"products": {"product": 0}}},
            )
        )
        assert values
        counter += 1
        assert list(values[0].keys()) == keys
        assert all("product" not in val.keys() for val in values[0]["batch"]["products"])
    assert counter == 10


def test_exclude_in_iterator():
    counter = 0
    for d_point in data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().dict_search(
                d_point,
                select_dict={"port_route": {"port": 0}},
            )
        )
        assert values
        counter += 1
        assert list(values[0].keys()) == keys
        port_route = values[0]["port_route"]
        if port_route:
            assert all({"days": mock.ANY} == port for port in port_route)
    assert counter == 10
