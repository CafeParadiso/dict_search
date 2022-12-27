from collections import abc
from pprint import pprint

from src.dict_search.dict_search import DictSearch
from src.dict_search.operators import exceptions
from src.dict_search import exceptions as search_exceptions

from test.new_fixtures import read_fixtures
from test.utils import TestCase


class TestArraySelectors(TestCase):
    def test_index(self):
        q = "Porsche"
        values, other_values = self.matching_test(match_query={"cargo": {"products": {"$index": [0, {"product": q}]}}})
        assert values
        for v in values:
            assert v["cargo"]["products"][0]["product"] == q
        for v in other_values:
            assert v["cargo"]["products"][0]["product"] != q

    def test_index_eq(self):
        q = 2.2
        values, other_values = self.matching_test(match_query={"checksum": {"$index": [0, q]}})
        assert values
        for v in values:
            assert v["checksum"][0] == q
        for v in other_values:
            assert v["checksum"][0] != q

    def test_index_multiple(self):
        q = [2.2, 2.2]
        values, other_values = self.matching_test(match_query={"checksum": {"$index": [[0, -1], q]}})
        for v in values:
            assert [v["checksum"][0], v["checksum"][-1]] == q
        for v in other_values:
            assert not ([v["checksum"][0], v["checksum"][-1]] == q)

    def test_index_multiple_length_one(self):
        q = [2.2]
        values, other_values = self.matching_test(match_query={"checksum": {"$index": [[0], q]}})
        for v in values:
            assert [v["checksum"][0]] == q
        for v in other_values:
            assert [v["checksum"][0]] != q

    def test_index_multiple_mixed_length_data(self):
        values, other_values = self.matching_test(
            match_query={"taxes": {"$index": [[0, 3], {"$any": {"type": "Bribe"}, "$func": lambda x: len(x) == 2}]}}
        )
        k = "taxes"
        for v in other_values:
            if k in v and v[k][0]["type"] == "Bribe":
                assert len(v[k]) < 4
        for val in values:
            assert len(val[k]) >= 4
            assert any(v["type"] == "Bribe" for v in val[k])

    def test_index_multiple_empty(self):
        assert not self.filter_results(DictSearch({"checksum": {"$index": [[8, 10], [2.2, 2.2]]}}), self.data)

    def test_index_error(self):
        q = 2.2
        s = self.get_search(match_query={"checksum": {"$index": [12, {"$all": q}]}})
        values = self.filter_results(s, self.data)
        assert isinstance(values, list) and not values

    def test_index_generator(self):
        q = "Shangai"
        search = DictSearch(match_query={"ports": {"$index": [0, {"port": q}]}})
        with self.assertRaises(TypeError):
            assert isinstance(self.data[0]["ports"], abc.Iterator)
            search(self.data[0])
        assert isinstance(self.data[0]["ports"], abc.Iterator)
        search.consumable_iterators = abc.Iterator
        same_data = read_fixtures()
        count = 0
        for d_p in same_data:
            assert isinstance(d_p["ports"], abc.Iterator)
            val = search(d_p)
            assert isinstance(d_p["ports"], search.cast_type_iterators)
            if val is not None:
                count += 1
                assert val["ports"][0]["port"] == q
        assert count > 0

    def test_slice(self):
        q = "Mustang"
        values, other_values = self.matching_test(
            match_query={"cargo": {"products": {"$slice": [":2", {"$all": {"product": q}}]}}}
        )
        assert values
        for val in values:
            assert all([v["product"] == q for v in val["cargo"]["products"][:2]])
        for val in other_values:
            assert not all([v["product"] == q for v in val["cargo"]["products"][:2]])

    def test_slice_eq(self):
        q = [2.2]
        values, other_values = self.matching_test(match_query={"checksum": {"$slice": [":1", q]}})
        assert values
        for v in values:
            assert v["checksum"][:1] == q
        for v in other_values:
            assert v["checksum"][:1] != q

    def test_slice_empty(self):
        q = [1]
        data = [{"a": []}, {"a": [1, 2, 3]}, {"a": []}]
        search = DictSearch({"a": {"$slice": [":1", q]}})
        values = list(filter(lambda x: x is not None, map(lambda x: search(x), data)))
        assert len(values) == 1 and data[1]["a"][:1] == q

    def test_slice_generator(self):
        q = [{"port": "Rotterdam", "days": 35}, "Busan"]
        search = DictSearch(match_query={"ports": {"$slice": [":2", q]}})
        with self.assertRaises(TypeError):
            assert isinstance(self.data[0]["ports"], abc.Iterator)
            search(self.data[0])
        assert isinstance(self.data[0]["ports"], abc.Iterator)
        search.consumable_iterators = abc.Iterator
        same_data = read_fixtures()
        count = 0
        for d_p in same_data:
            assert isinstance(d_p["ports"], abc.Iterator)
            val = search(d_p)
            assert isinstance(d_p["ports"], search.cast_type_iterators)
            if val is not None:
                count += 1
                assert val["ports"][:2] == q
        assert count > 0

    def test_slice_all_patterns(self):
        search = DictSearch()
        data = {"a": [0, 1, 2, 3, 4, 5]}
        for slice_str, assert_result in [
            ("2:", data["a"][2:]),
            ("2::", data["a"][2::]),
            (":2", data["a"][:2]),
            (":2:", data["a"][:2:]),
            ("::2", data["a"][::2]),
            ("2:4", data["a"][2:4]),
            ("2:4:", data["a"][2:4:]),
            ("2::2", data["a"][2::2]),
            (":4:2", data["a"][:4:2]),
            ("2:5:2", data["a"][2:5:2]),
        ]:
            search.match_query = {"a": {"$slice": [slice_str, assert_result]}}
            result = search(data)
            assert result and eval(f"result['a'][{slice_str}]", {"result": result}) == assert_result

    def test_where(self):
        q = [{"product": "Kawasaki"}, {"$any": {"status": "Finished"}}]
        values, other_values = self.matching_test(match_query={"cargo": {"products": {"$where": q}}})
        for v in values:
            products = v["cargo"]["products"]
            assert any(p["status"] == "Finished" and p["product"] == "Kawasaki" for p in products if "status" in p)
        for v in other_values:
            products = v["cargo"]["products"]
            assert not any(p["status"] == "Finished" and p["product"] == "Kawasaki" for p in products if "status" in p)

    def test_where_eq(self):
        from datetime import datetime

        a = [
            {
                "due_delivery": datetime(2022, 11, 27, 0, 0),
                "origin": "Zimbawe",
                "product": "Kawasaki",
                "status": "Finished",
                "suspicious": "no",
                "uuid": "81719c70-abbb-489b-9590-6fc8618a9ede",
                "variations": [{"type": "B", "units": 100}, {"type": "D", "units": 63}],
                "weight": 1282,
            }
        ]
        q = [{"product": "Kawasaki"}, a]
        values, other_values = self.matching_test(match_query={"cargo": {"products": {"$where": q}}})
        for v in values:
            products = v["cargo"]["products"]
            assert products == a
        for v in other_values:
            products = v["cargo"]["products"]
            assert products != a

    def test_where_generator(self):
        q = [{"port": "Shenzen"}, {"$any": {"days": 20}}]
        search = DictSearch(match_query={"ports": {"$where": q}}, consumable_iterators=abc.Iterator)
        same_data = read_fixtures()
        count = 0
        for d_p in same_data:
            assert isinstance(d_p["ports"], abc.Iterator)
            val = search(d_p)
            assert isinstance(d_p["ports"], search.cast_type_iterators)
            if val is not None:
                count += 1
                assert {"port": "Shenzen", "days": 20}
        assert count > 0

    def test_where_no_match(self):
        data = [
            {"a": [{"b": 1, "c": False}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
            {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
        ]
        search = DictSearch({"a": {"$where": [{"x": 1}, {"c": True}]}})
        values = list(filter(lambda x: x is not None, map(lambda x: search(x), data)))
        assert not values

    def test_where_empty(self):
        data = [
            {"a": [{"b": 1, "c": False}, {"b": 0, "c": False}, {"b": 1, "c": 12}]},
            {"a": [{"b": 1, "c": True}, {"b": 0, "c": False}, {"b": 1, "c": True}]},
            {"a": []},
        ]
        search = DictSearch({"a": {"$where": [{"b": 1}, {"$any": {"c": True}}]}})
        values = list(filter(lambda x: x is not None, map(lambda x: search(x), data)))
        assert values[0] == data[1]


class TestExceptions(TestCase):
    def test_where_precondition(self):
        with self.assertRaises(exceptions.WhereOperatorError):
            DictSearch({"ports": {"$where": {1, 2}}})

    def test_where_generator_error(self):
        q = [{"port": "Shenzen"}, {"$any": {"days": 20}}]
        search = DictSearch(match_query={"ports": {"$where": q}})
        with self.assertRaises(exceptions.WhereIteratorException):
            assert isinstance(self.data[0]["ports"], abc.Iterator)
            search(self.data[0])

    def test_slice_type_precondition(self):
        with self.assertRaises(exceptions.ArraySelectorFormatException):
            DictSearch({"$slice": {1, 2}})

    def test_slice_len_precondition(self):
        with self.assertRaises(exceptions.SliceSelectionOperatorError):
            DictSearch({"$slice": [1]})

    def test_slice_pattern_precondition(self):
        with self.assertRaises(exceptions.SliceSelectionOperatorError):
            DictSearch({"$slice": ["::", [2]]})
