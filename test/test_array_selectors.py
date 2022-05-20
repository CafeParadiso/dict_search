from pprint import pprint

from src.dict_search.dict_search import DictSearch

from . import data


# TODO test with data being a generator

def test_index():
    values = DictSearch().dict_search(
        data.complex_data,
        {"posts": {"$index": {"0": {"interacted": {"$index": {"-1": {"type": "share"}}}}}}},
    )
    pprint(list(values))


def test_index_empty_container():
    values = list(DictSearch().dict_search(
        [{"a": []}, {"a": [1]}],
        {"a": {"$index": {0: 1}}},
    ))
    pprint(values)


def test_range():
    for range_str, val, assert_val in [
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
        values = DictSearch().dict_search(
            data.range_data, {"mixed": {"a": {"$range": {range_str: {"$expr": lambda x: x.count(2) == val}}}}}
        )
        assert len(list(values)) == assert_val


def test_where():
    values = DictSearch().dict_search(
       data.student_data, {"info": {"mentions": {"$where": [{"type": "angry"}, {"$all": {"score": 5}}]}}},
    )
    pprint(list(values))


def test_where_eq():
    values = DictSearch().dict_search(
        data.student_data,
        {"c": "Territori", "tt": {"t": {"ff": {"f": {"$where": {"c": "Altitud"}}}}}},
    )
    pprint(list(values))

#def test_where_eq_type_error
#def test_where_not_found
#def test_where_complex