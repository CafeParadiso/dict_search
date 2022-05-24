from pprint import pprint

from src.dict_search.dict_search import DictSearch

from . import data


# TODO test with data being a generator


def test_index():
    results = DictSearch().dict_search(
        data.complex_data,
        {"posts": {"$index": {"0": {"interacted": {"$index": {"-1": {"type": "share"}}}}}}},
    )
    pprint(list(results))


def test_index_eq():
    results = list(
        DictSearch().dict_search(
            [{"a": [2]}, {"a": [1]}],
            {"a": {"$index": {0: 1}}},
        )
    )
    assert len(results) == 1


def test_index_empty_data():
    results = list(
        DictSearch().dict_search(
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
        results = list(DictSearch().dict_search(
            data.range_data, {"mixed": {"a": {"$range": {range_str: {"$expr": lambda x: x.count(2) == val}}}}}
        ))
        assert len(results) == assert_result


def test_range_eq():
    results = list(
        DictSearch().dict_search(
            [{"a": [0, 1, 2, 3]}, {"a": [1, 2, 3, 4]}],
            {"a": {"$range": {":2": [0, 1]}}},
        )
    )
    assert len(results) == 1


def test_range_empty():
    results = list(
        DictSearch().dict_search(
            [{"a": []}, {"a": [1, 2, 3, 4]}],
            {"a": {"$range": {":2": [0, 1]}}},
        )
    )
    assert not results


def test_range_bad_format():
    results = list(
        DictSearch().dict_search(
            data.range_data, {"mixed": {"a": {"$range": {"a": {"$expr": lambda x: x.count(2) == 1}}}}}
        )
    )
    assert not results


def test_where():
    results = list(DictSearch().dict_search(
        data.student_data,
        {"info": {"mentions": {"$where": [{"type": "angry"}, {"$all": {"score": 5}}]}}},
    ))
    assert len(results) == 1


def test_where_type_error():
    results = list(DictSearch().dict_search(
        [
            {"a": [{"b": 1, "c": False}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
            {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]}
        ],
        {"a": {"$where": [{"b": 1}, data.CursedData()]}}
    ))
    assert not results


def test_where_no_match():
    results = list(DictSearch().dict_search(
        [
            {"a": [{"b": 1, "c": False}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
            {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]}
        ],
        {"a": {"$where": [{"x": 1}, {"c": True}]}}
    ))
    assert not results


def test_where_and_array_op():
    results = list(DictSearch().dict_search(
        [
            {"a": []},
            {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": False}]},
            {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]}
        ],
        {"a": {"$where": [{"b": 1}, {"$matchgte": {1: {"c": True}}}]}}
    ))
    assert len(results) == 2


def test_where_empty():
    results = list(DictSearch().dict_search(
        [
            {"a": []},
            {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]}
        ],
        {"a": {"$where": [{"b": 1}, {"$all": {"c": True}}]}}
    ))
    assert len(results) == 1
