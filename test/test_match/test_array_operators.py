from collections.abc import Iterator
from src.dict_search.dict_search import DictSearch

from test.utils import TestCase, read_fixtures


class TestArrayOperators(TestCase):
    def test_start_iterator(self):
        q = {"port": "Shangai"}
        search = DictSearch()
        for op in search.array_operators:
            for dp, original_dp in zip(self.data, read_fixtures()):
                if "count" in op:
                    search.match_query = {"ports": {op: {1: q}}}
                else:
                    search.match_query = {"ports": {op: q}}
                search(dp)
                assert isinstance(dp["ports"], Iterator) and isinstance(original_dp["ports"], Iterator)
                original_ports = list(original_dp["ports"])
                ports = list(dp["ports"])
                if original_ports:
                    assert ports != original_dp["ports"]

    def test_emtpy_array_data(self):
        data = [{"values": [0, 1, 1]}, {"values": [1, 1, 1]}, {"values": []}, {"values": [0, 0, 2]}]
        search = DictSearch(match_query={"values": {"$all": {"$inst": int}}})
        for d_point in data:
            if search(d_point) is not None:
                assert d_point["values"] != []
        data = [{"values": [0, 1, 1]}, {"values": [1, 1, 1]}, {"values": []}, {"values": [0, 0, 2]}]
        search = DictSearch(match_query={"values": {"$any": {"$inst": int}}})
        for d_point in data:
            if search(d_point) is not None:
                assert d_point["values"] != []

    def test_all(self):
        q = "BMW"
        values, other_values = self.matching_test(match_query={"cargo": {"products": {"$all": {"product": q}}}})
        assert isinstance(values, list) and values
        products = [prod["product"] for products in values for prod in products["cargo"]["products"]]
        assert all(prod == q for prod in products)
        other_products = [prod["product"] for products in other_values for prod in products["cargo"]["products"]]
        assert not all(prod == q for prod in other_products)

    def test_all_eq(self):
        q = {"type": "Bribe", "value": 11}
        values = self.matching_test(match_query={"taxes": {"$all": q}})[0]
        assert values
        other_values = self.matching_test(match_query={"taxes": {"$all": {"$eq": q}}})[0]
        assert other_values
        assert values != other_values

    def test_any(self):
        q = "BMW"
        values, other_values = self.matching_test(match_query={"cargo": {"products": {"$any": {"product": q}}}})
        assert isinstance(values, list) and values
        for val in values:
            products = [prod["product"] for prod in val["cargo"]["products"]]
            assert q in products
        for val in other_values:
            products = [prod["product"] for prod in val["cargo"]["products"]]
            assert q not in products

    def test_any_eq(self):
        q = 1
        values, other_values = self.matching_test(match_query={"checksum": {"$any": 1}})
        for val in values:
            assert any(v == q for v in val["checksum"])
        for val in other_values:
            assert not any(v == q for v in val["checksum"])

    def test_count_eq(self):
        q = 1
        n = 1
        values, other_values = self.matching_test(match_query={"checksum": {"$count": {n: q}}})
        assert isinstance(values, list) and values
        for val in values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) == n
        for val in other_values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) != n

    def test_countgt(self):
        q = "Peru"
        n = 1
        values, other_values = self.matching_test(match_query={"cargo": {"products": {"$countgt": {n: {"origin": q}}}}})
        assert isinstance(values, list) and values
        for val in values:
            origin = [p["origin"] for p in val["cargo"]["products"]]
            assert origin.count(q) > n
        for val in other_values:
            origin = [p["origin"] for p in val["cargo"]["products"]]
            assert origin.count(q) <= n

    def test_countgt_eq(self):
        q = 1
        n = 1
        values, other_values = self.matching_test(match_query={"checksum": {"$countgt": {n: q}}})
        assert isinstance(values, list) and values
        for val in values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) > n
        for val in other_values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) <= n

    def test_countgte(self):
        q = "Peru"
        n = 1
        values, other_values = self.matching_test(
            match_query={"cargo": {"products": {"$countgte": {n: {"origin": q}}}}}
        )
        assert isinstance(values, list) and values
        for val in values:
            origin = [p["origin"] for p in val["cargo"]["products"]]
            assert origin.count(q) >= n
        for val in other_values:
            origin = [p["origin"] for p in val["cargo"]["products"]]
            assert origin.count(q) < n

    def test_countgte_eq(self):
        q = 1
        n = 1
        values, other_values = self.matching_test(match_query={"checksum": {"$countgte": {n: q}}})
        assert isinstance(values, list) and values
        for val in values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) >= n
        for val in other_values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) < n

    def test_countlt(self):
        q = "Peru"
        n = 1
        values, other_values = self.matching_test(match_query={"cargo": {"products": {"$countlt": {n: {"origin": q}}}}})
        assert isinstance(values, list) and values
        for val in values:
            origin = [p["origin"] for p in val["cargo"]["products"]]
            assert origin.count(q) < n
        for val in other_values:
            origin = [p["origin"] for p in val["cargo"]["products"]]
            assert origin.count(q) >= n

    def test_countglt_eq(self):
        q = 1
        n = 1
        values, other_values = self.matching_test(match_query={"checksum": {"$countlt": {n: q}}})
        assert isinstance(values, list) and values
        for val in values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) < n
        for val in other_values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) >= n

    def test_countlte(self):
        q = "Peru"
        n = 1
        values, other_values = self.matching_test(
            match_query={"cargo": {"products": {"$countlte": {n: {"origin": q}}}}}
        )
        for val in values:
            origin = [p["origin"] for p in val["cargo"]["products"]]
            assert origin.count(q) <= n
        for val in other_values:
            origin = [p["origin"] for p in val["cargo"]["products"]]
            assert origin.count(q) > n

    def test_countglte_eq(self):
        q = 1
        n = 1
        values, other_values = self.matching_test(match_query={"checksum": {"$countlte": {n: q}}})
        assert isinstance(values, list) and values
        for val in values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) <= n
        for val in other_values:
            origin = [c for c in val["checksum"]]
            assert origin.count(q) > n
