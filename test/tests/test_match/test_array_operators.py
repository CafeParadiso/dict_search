from collections.abc import Iterator
from src.dict_search.dict_search import DictSearch
from datetime import datetime

from test.utils import BaseTestOperators as Base
from test.new_fixtures.data import PROD_GR, PROD_CAR, PORT_VAL


class TestAll(Base.SearchMixin):
    sub_query = {"product": PROD_GR, "due_date": datetime(2022, 7, 1), "cost": 10**6}
    search_checks = [
        (DictSearch(match_query={"products": {"$all": {"product": PROD_CAR}}}), lambda x: all(y["product"] == PROD_CAR for y in x["products"]) if x["products"] else False),
        (DictSearch(match_query={"products": {"$all": sub_query}}), lambda x: all(y == TestAll.sub_query for y in x["products"]) if x["products"] else False),
    ]

    def test_start_iterator(self):
        result_count = 0
        search = DictSearch(match_query={"port_route": {"$all": PORT_VAL}})
        for dp, original_dp in zip(self.data, self.data):
            result = search(dp)
            if result:
                assert isinstance(result["port_route"], Iterator)
                assert list(result["port_route"]) != list(original_dp["port_route"])
                result_count += 1
        assert result_count

    def test_emtpy_array_data(self):
        data = [{"values": [0, 1, 1]}, {"values": [1, 1, 1]}, {"values": []}, {"values": [0, 0, 2]}]
        search = DictSearch(match_query={"values": {"$all": {"$inst": int}}})
        for d_point in data:
            if search(d_point) is not None:
                assert d_point["values"] != []


class TestAny(Base.SearchMixin):
    sub_query = {"product": PROD_GR, "due_date": datetime(2022, 7, 1), "cost": 10**6}
    search_checks = [
        (DictSearch(match_query={"products": {"$any": {"product": PROD_CAR}}}), lambda x: any(y["product"] == PROD_CAR for y in x["products"])),
        (DictSearch(match_query={"products": {"$any": sub_query}}), lambda x: any(y == TestAll.sub_query for y in x["products"])),
    ]

    def test_start_iterator(self):
        result_count = 0
        search = DictSearch(match_query={"port_route": {"$any": PORT_VAL}})
        for dp, original_dp in zip(self.data, self.data):
            result = search(dp)
            if result:
                assert isinstance(result["port_route"], Iterator)
                assert list(result["port_route"]) != list(original_dp["port_route"])
                result_count += 1
        assert result_count

    def test_emtpy_array_data(self):
        data = [{"values": [0, 1, 1]}, {"values": [1, 1, 1]}, {"values": []}, {"values": [0, 0, 2]}]
        search = DictSearch(match_query={"values": {"$any": {"$inst": int}}})
        for d_point in data:
            if search(d_point) is not None:
                assert d_point["values"] != []
