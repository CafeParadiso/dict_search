from unittest import mock

from src.dict_search.dict_search import DictSearch
from .fixtures import data as test_data


def test_malformed():
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={"id": "1"},
        )
    )
    assert not values


def test_mixed_include():
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={"id": 1, "batch": 0},
        )
    )
    assert len(values) == 10 and all({"id": mock.ANY} == v for v in values)


def test_mixed_exclude():
    for d_point in test_data.read_fixtures():
        initial_keys = list(d_point.keys())
        values = list(DictSearch().__call__(d_point, select_dict={"id": 0, "batch": 1}))
        initial_keys.remove("id")
        assert initial_keys == list(values[0].keys())


def test_include_missing_key():
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={"missing": 1},
        )
    )
    assert not values
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={"id": 1, "missing": 1},
        )
    )
    assert len(values) == 10 and values == [{"id": i} for i, v in enumerate(values)]


def test_include_one():
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={"id": 1},
        )
    )
    assert len(values) == 10 and values == [{"id": i} for i, v in enumerate(values)]


def test_include_multiple():
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={"paid": 1, "id": 1},
        )
    )
    assert len(values) == 10 and all({"id": mock.ANY, "paid": mock.ANY} == v for v in values)


def test_include_nested():
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={"info": {"origin": 1}, "id": 1},
        )
    )
    assert len(values) == 10 and all({"info": {"origin": mock.ANY}, "id": mock.ANY} == v for v in values)


def test_include_in_list():
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={
                "batch": {"products": {"types": {"$array": {"price": 1}}}},
                "id": 1,
            },
        )
    )
    assert len(values) == 10
    for i, val in enumerate(values):
        if "batch" in val:
            assert val == {"id": i, "batch": {"products": mock.ANY}}
            assert "price" in val["batch"]["products"][0]["types"][0]
        else:
            assert val == {"id": i}


def test_include_in_iterator():
    data = list(test_data.read_fixtures())
    values = list(
        DictSearch().__call__(
            data,
            select_dict={"port_route": {"$array": {"port": 1}}},
        )
    )
    assert len(values) == 8
    assert all({"port": mock.ANY} == v for val in values for v in val["port_route"])


def test_exclude_missing_key():
    values = list(
        DictSearch().__call__(
            test_data.read_fixtures(),
            select_dict={"missing": 0},
        )
    )
    assert not values
    for d_point in test_data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"id": 0, "missing": 0},
            )
        )
        assert values
        keys.remove("id")
        assert list(values[0].keys()) == keys


def test_exclude_one():
    counter = 0
    for d_point in test_data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().__call__(
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
    for d_point in test_data.read_fixtures():
        initial_keys = list(d_point.keys())
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": 0, "id": 0},
            )
        )
        assert values
        counter += 1
        [initial_keys.remove(k) for k in ["batch", "id"]]
        assert list(values[0].keys()) == initial_keys
    assert counter == 10


def test_exclude_nested():
    counter = 0
    for d_point in test_data.read_fixtures():
        keys = list(d_point.keys())
        info_keys = list(d_point["info"].keys())
        values = list(
            DictSearch().__call__(
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
    for d_point in test_data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"batch": {"products": {"$array": {"product": 0}}}},
            )
        )
        assert values
        counter += 1
        assert list(values[0].keys()) == keys
        assert all("product" not in val.keys() for val in values[0]["batch"]["products"])
    assert counter == 10


def test_exclude_in_iterator():
    counter = 0
    for d_point in test_data.read_fixtures():
        keys = list(d_point.keys())
        values = list(
            DictSearch().__call__(
                d_point,
                select_dict={"port_route": {"$array": {"port": 0}}},
            )
        )
        if values:
            counter += 1
            assert list(values[0].keys()) == keys
            port_route = values[0]["port_route"]
            if port_route:
                assert all({"days": mock.ANY} == port for port in port_route)
    assert counter == 8
