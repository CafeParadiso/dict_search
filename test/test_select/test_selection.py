from collections import abc
from unittest import mock

from src.dict_search.dict_search import DictSearch
from src.dict_search import exceptions
from test.utils import TestCase, read_fixtures


class TestSelection(TestCase):
    def test_value_error(self):
        with self.assertRaises(exceptions.SelectValueError):
            for dp, original_dp in self.selection_test({"id": "3"}):
                print(dp)

    def test_mixed_include(self):
        with self.assertRaises(exceptions.SelectMixedError):
            for dp, original_dp in self.selection_test({"id": 1, "info": 0}):
                print(dp)

    def test_include_missing_key(self):
        for dp, original_dp in self.selection_test({"missing": 1}):
            assert dp is None

    def test_include_one(self):
        for dp, original_dp in self.selection_test({"id": 1}):
            assert dp == {"id": mock.ANY}

    def test_include_multiple(self):
        for dp, original_dp in self.selection_test({"id": 1, "info": 1}):
            assert dp == {"id": mock.ANY, "info": mock.ANY}

    def test_include_nested(self):
        for dp, original_dp in self.selection_test({"id": 1, "info": {"origin": 1}}):
            assert dp == {"id": mock.ANY, "info": {"origin": mock.ANY}}

    def test_include_iterator(self):
        search = DictSearch({"ports": {"$array": {"port": 1}}})
        for index, dp in enumerate(read_fixtures()):
            assert isinstance(dp["ports"], abc.Iterator)
            sel = search(dp)
            assert isinstance(dp["ports"], abc.Iterator)
            if sel is not None:
                assert sel == {"ports": mock.ANY}
                assert all({"port": mock.ANY} == port for port in sel["ports"])
                original_data = list(read_fixtures())[index]
                assert isinstance(original_data["ports"], abc.Iterator)
                original_ports = list(original_data["ports"])
                if original_ports:
                    assert list(dp["ports"]) != original_ports

    def test_mixed_exclude(self):
        with self.assertRaises(exceptions.SelectMixedError):
            for dp, original_dp in self.selection_test({"id": 0, "info": 1}):
                print(dp)

    def test_exclude_missing_key(self):
        for dp, original_dp in self.selection_test({"missing": 0}):
            assert dp is None

    def test_exclude_one(self):
        for dp, original_dp in self.selection_test({"id": 0}):
            assert dp == {k: v for k, v in original_dp.items() if k != "id"}

    def test_exclude_multiple(self):
        for dp, original_dp in self.selection_test({"id": 0, "info": 0}):
            assert dp == {k: v for k, v in original_dp.items() if k not in ["id", "info"]}

    def test_exclude_nested(self):
        for dp, original_dp in self.selection_test({"id": 0, "info": {"origin": 0}}):
            assert_data = {k: v for k, v in original_dp.items() if k not in ["id", "info"]}
            assert_data["info"] = {k: v for k, v in original_dp["info"].items() if k not in ["origin"]}
            assert dp == assert_data

    def test_exclude_empty(self):
        data = [{"a": 1, "b": {"a": 3}}, {"a": 1, "x": 1}, {"b": {"a": 4}}, {"b": {"a": 4}, "c": {"d": 3}}]
        search = DictSearch(select_query={"a": 0, "b": {"a": 0}, "c": {"d": 0}})
        results = self.filter_results(search, data)
        assert results == [{"b": {}}, {"x": 1}, {"b": {}}, {"b": {}, "c": {}}]

    def test_array_exclude(self):
        for dp, original_dp in self.selection_test({"cargo": {"products": {"$array": {"product": 0}}}}):
            if dp is not None:
                assert_data = {k: v for k, v in original_dp.items() if k not in ["cargo"]}
                assert_data["cargo"] = {
                    "products": [
                        {k: v for k, v in prod.items() if k not in ["product"]}
                        for prod in original_dp["cargo"]["products"]
                    ]
                }
                assert dp == assert_data

    def test_array_mixed(self):
        data = [{"a": [1, {"a": 3}, {"a": 2, "b": 4}]}, {"a": []}, {"a": 1}]
        search = DictSearch(select_query={"a": {"$array": {"a": 0}}})
        results = self.filter_results(search, data)
        assert results == [{"a": [{"b": 4}]}]
        search = DictSearch(select_query={"a": {"$array": {"a": 1}}})
        results = self.filter_results(search, data)
        assert results == [{"a": [{"a": 3}, {"a": 2}]}]

    def test_array_included(self):
        for dp, original_dp in self.selection_test({"cargo": {"products": {"$array": {"product": 1}}}}):
            if dp is not None:
                assert dp == {"cargo": {"products": mock.ANY}}
                for val in dp["cargo"]["products"]:
                    assert val == {"product": mock.ANY}

    def test_exclude_iterator(self):
        search = DictSearch({"ports": {"$array": {"port": 0}}})
        for index, dp in enumerate(read_fixtures()):
            assert isinstance(dp["ports"], abc.Iterator)
            sel = search(dp)
            assert isinstance(dp["ports"], abc.Iterator)
            if sel is not None:
                assert_data = {k: v for k, v in dp.items() if k not in ["ports"]}
                assert_data["ports"] = [{"days": mock.ANY} for x in range(len(sel["ports"]))]
                assert sel == assert_data
                original_data = list(read_fixtures())[index]
                assert isinstance(original_data["ports"], abc.Iterator)
                original_ports = list(original_data["ports"])
                if original_ports:
                    assert list(dp["ports"]) != original_ports
