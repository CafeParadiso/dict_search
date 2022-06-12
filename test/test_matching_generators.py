import types

from src.dict_search.dict_search import DictSearch


def test_unpack_iterator():
    print(list(
        DictSearch().dict_search(
            [
                {"a": (x for x in ["Sydney", "Moscow"]), "b": 1},
                {"a": (x for x in ["Bcn", "Sydney"]), "b": 2},
                {"a": (x for x in ["Bcn", "Svq"]), "b": 3},
                {"a": (x for x in []), "b": 3},
            ],
            {"a": {"$any": "Bcn"}},
        )
    ))


def test_literal_iterator():
    v = list(
        DictSearch().dict_search(
            [
                {"a": (x for x in ["Sydney", "Moscow"]), "b": 1},
                {"a": (x for x in ["Bcn", "Sydney"]), "b": 2},
                {"a": (x for x in ["Bcn", "Svq"]), "b": 3},
                {"a": "cat", "b": 3},
            ],
            {"a": {"$inst": types.GeneratorType}},
        )
    )
    print([dikt["a"] for dikt in v])
    assert len(v) == 3 and all(isinstance(dikt["a"], types.GeneratorType) for dikt in v)


def test_exhaustible_iterator():
    v = list(
        DictSearch(consumable_iterator=types.GeneratorType).dict_search(
            [
                {"a": (x for x in ["Sydney", "Moscow"]), "b": 1},
                {"a": (x for x in ["Bcn", "Sydney"]), "b": 2},
                {"a": (x for x in ["Bcn", "Svq"]), "b": 3},
                {"a": (x for x in []), "b": 3},
            ],
            {"a": {"$any": "Bcn"}},
        )
    )
    assert all(len(list(val["a"])) == 1 for val in v)
