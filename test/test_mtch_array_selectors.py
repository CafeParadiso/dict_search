from pprint import pprint

from pytest import raises as pytest_raises

from src.dict_search.dict_search import DictSearch
from src.dict_search import exceptions

from .fixtures import data


def test_array_selector_exception():
    with pytest_raises(exceptions.ArraySelectorFormatException):
        list(
            DictSearch().__call__(
                data.complex_data,
                {"posts": {"$index": 1}},
            )
        )


def test_index():
    results = DictSearch().__call__(
        data.complex_data,
        {"posts": {"$index": {"0": {"interacted": {"$index": {"-1": {"type": "share"}}}}}}},
    )
    pprint(list(results))


def test_index_eq():
    results = list(
        DictSearch().__call__(
            [{"a": [2]}, {"a": [1]}],
            {"a": {"$index": {0: 1}}},
        )
    )
    assert len(results) == 1


def test_index_multiple():
    results = list(
        DictSearch().__call__(
            [{"a": [1, 2, 3, 4, 5]}, {"a": [3, 4, 5, 6, 7, 8]}],
            {"a": {"$index": [[0, -1], {"$expr": lambda x: x == [1, 5]}]}},
        )
    )
    pprint(results)


def test_index_empty_data():
    results = list(
        DictSearch().__call__(
            [{"a": []}, {"a": []}],
            {"a": {"$index": {0: 1}}},
        )
    )
    assert not results


def test_range():
    for range_str, val, assert_result in [
        ("2:", 3, 2),
        ("2::", 3, 2),
        (":2", 2, 1),
        (":2:", 2, 1),
        ("::2", 1, 1),
        ("2:6", 3, 2),
        ("2:4:", 2, 2),
        ("2::2", 1, 3),
        (":4:2", 2, 2),
        ("2:5:2", 1, 3),
    ]:
        print(range_str)
        results = list(
            DictSearch().__call__(
                data.range_data, {"mixed": {"a": {"$range": {range_str: {"$expr": lambda x: x.count(2) == val}}}}}
            )
        )
        assert len(results) == assert_result


def test_range_eq():
    results = list(
        DictSearch().__call__(
            [{"a": [0, 1, 2, 3]}, {"a": [1, 2, 3, 4]}],
            {"a": {"$range": {":2": [0, 1]}}},
        )
    )
    assert len(results) == 1


def test_range_empty():
    results = list(
        DictSearch().__call__(
            [{"a": []}, {"a": [1, 2, 3, 4]}],
            {"a": {"$range": {":2": [0, 1]}}},
        )
    )
    assert not results


def test_range_bad_format():
    with pytest_raises(exceptions.RangeSelectionOperatorError):
        results = list(
            DictSearch().__call__(
                data.range_data, {"mixed": {"a": {"$range": {"a": {"$expr": lambda x: isinstance(x, list)}}}}}
            )
        )
        assert not results


def test_where():
    results = list(
        DictSearch().__call__(
            data.student_data,
            {"info": {"mentions": {"$where": [{"type": "angry"}, {"$all": {"score": 5}}]}}},
        )
    )
    assert len(results) == 1


def test_where_type_error():
    results = list(
        DictSearch(low_level_glob_exc=Exception).__call__(
            [
                {"a": [{"b": 1, "c": False}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
                {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
            ],
            {"a": {"$where": [{"b": 1}, data.CursedData()]}},
        )
    )
    assert not results


def test_where_no_match():
    results = list(
        DictSearch().__call__(
            [
                {"a": [{"b": 1, "c": False}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
                {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
            ],
            {"a": {"$where": [{"x": 1}, {"c": True}]}},
        )
    )
    assert not results


def test_where_and_array_op():
    results = list(
        DictSearch().__call__(
            [
                {"a": []},
                {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": False}]},
                {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
            ],
            {"a": {"$where": [{"b": 1}, {"$matchgte": {1: {"c": True}}}]}},
        )
    )
    assert len(results) == 2


def test_where_empty():
    results = list(
        DictSearch().__call__(
            [{"a": []}, {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]}],
            {"a": {"$where": [{"b": 1}, {"$all": {"c": True}}]}},
        )
    )
    assert len(results) == 1


def test_where_malformed_exceptions():
    with pytest_raises(exceptions.PreconditionError):
        values = list(
            DictSearch().__call__(
                data.student_data,
                {"info": {"mentions": {"$where": [1, 2]}}},
            )
        )
        pprint(values)


def test_where_malfored():
    values = list(
        DictSearch().__call__(
            data.student_data,
            {"info": {"mentions": {"$where": [{}, 1]}}},
        )
    )
    assert not values


def test_where_exception():
    with pytest_raises(exceptions.WhereOperatorError):
        list(
            DictSearch().__call__(
                data.student_data,
                {"info": {"mentions": {"$where": {"a": 1}}}},
            )
        )


def generator(values):
    for val in range(values):
        yield val


def test_data_generator():
    vals = list(DictSearch().__call__([{"a": generator(4), "b": generator(3)}], {"a": {"$any": 3}}))
    pprint(vals)


def test_array_selector_and_other():
    values = DictSearch().__call__(
        data.complex_data,
        {
            "values": {"$all": {"$gt": 0.5}},
            "user": {"id": {"$lt": 100}},
        },
    )
    values = list(values)
    assert len(values) == 2
    assert [val["user"]["id"] for val in values] == [94, 68]
