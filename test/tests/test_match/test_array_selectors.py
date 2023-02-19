from collections import abc
from datetime import datetime

from src.dict_search.dict_search import DictSearch
from src.dict_search.operators import exceptions
from src.dict_search.operators.operators import array_selectors as aop

from test.new_fixtures import data
from test.utils import BaseTestOperators as Base


class TestIndex(Base.SearchMixin, Base.ExceptionsMixin):
    exceptions = [
        (lambda: aop.Index("1"), exceptions.IndexTypeError),
        (lambda: aop.Index([1, "1"]), exceptions.IndexListError),
    ]
    search_checks = [
        (DictSearch({"containers": {"$index": [0, data.COMPANY_COSCO]}}), lambda x: x["containers"][0] == data.COMPANY_COSCO if x["containers"] else False), # test index equal
        (DictSearch({"products": {"$index": [0, {"product": data.PROD_CAR}]}}), lambda x: x["products"][0]["product"] == data.PROD_CAR if x["products"] else False), # test index sub key
        (DictSearch({"containers": {"$index": [[0], [data.COMPANY_COSCO]]}}), lambda x: x["containers"][0] == data.COMPANY_COSCO if x["containers"] else False), # test index single key as list
        (DictSearch({"containers": {"$index": [[0, 1], [data.COMPANY_COSCO, data.COMPANY_HL]]}}), lambda x: x["containers"][0] == data.COMPANY_COSCO and x["containers"][1] == data.COMPANY_HL if len(x["containers"]) >= 2 else False), # test index multiple
        (DictSearch({"containers": {"$index": [2, data.COMPANY_MSK]}}), lambda x: x["containers"][2] == data.COMPANY_MSK if len(x["containers"]) > 2 else False), # test index mixed length
        (DictSearch({"products": {"$index": [[0, 2], {"$all": {"$or": [{"product": data.PROD_CAR}, {"cost": 500000}]}}]}}), lambda x: x["products"][0]["product"] == data.PROD_CAR or x["products"][2]["cost"] == 500000 if len(x["products"]) > 2 else False), # test index multiple mixed length
        (DictSearch({"taxes": {"$index": [0, data.TAX_B]}}), lambda x: x["taxes"][0] == data.TAX_B if x["taxes"] and isinstance(x["taxes"], list) else False), # test empty
    ]

    def test_implementation(self):
        data = [0, 1, 2, 3]
        # single index
        op = aop.Index(1)
        self.assertEqual(1, op(data))
        # multiple index
        op = aop.Index([0, -1])
        self.assertEqual([0, 3], op(data))
        # single index as list
        op = aop.Index([1])
        self.assertEqual([1], op(data))

    def test_generator(self):
        generator_match_count = 0
        results, other_results = [], []
        search = DictSearch(match_query={"port_route": {"$index": [0, data.PORT_TANG]}})
        for i, d_point in enumerate(data.get_data()):
            if isinstance(d_point["port_route"], abc.Iterator):
                with self.assertRaises(TypeError):
                    search(d_point)
                search.consumable_iterators = abc.Iterator
                if search(d_point):
                    generator_match_count += 1
                    self.assertIsInstance(d_point["port_route"], list)
                    self.assertIn(data.PORT_TANG, list(d_point["port_route"]))
                    self.assertEqual(list(data.get_data()[i]["port_route"])[0], data.PORT_TANG)
                    results.append(d_point)
                search.consumable_iterators = None
            elif search(d_point):
                results.append(d_point)
        assert results
        assert generator_match_count


class TestSlice(Base.SearchMixin, Base.ExceptionsMixin):
    exceptions = [
        (lambda: DictSearch({"$slice": {1, 2}}), exceptions.ArraySelectorFormatException),
        (lambda: DictSearch({"$slice": [1]}), exceptions.ArraySelectorFormatException),
        (lambda: DictSearch({"$slice": ["::", [2]]}), exceptions.SliceSelectionOperatorError),
    ]
    search_checks = [
        (DictSearch(match_query={"containers": {"$slice": [":2", [data.COMPANY_COSCO, data.COMPANY_HL]]}}), lambda x: x["containers"][:2] == [data.COMPANY_COSCO, data.COMPANY_HL] if len(x["containers"]) >= 2 else False),  # slice equal
        (DictSearch(match_query={"containers": {"$slice": [":2", [data.COMPANY_COSCO, data.COMPANY_HL]]}}), lambda x: x["containers"][:2] == [data.COMPANY_COSCO, data.COMPANY_HL] if len(x["containers"]) >= 2 else False),  # slice
    ]

    def test_implementation(self):
        data = [0, 1, 2, 3]
        op = aop.Slice(":2")
        self.assertEqual(op(data), data[:2])

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

    def test_generator(self):
        generator_match_count = 0
        results, other_results = [], []
        search = DictSearch(match_query={"port_route": {"$slice": [":1", [data.PORT_TANG]]}})
        for i, d_point in enumerate(data.get_data()):
            if isinstance(d_point["port_route"], abc.Iterator):
                with self.assertRaises(TypeError):
                    search(d_point)
                search.consumable_iterators = abc.Iterator
                if search(d_point):
                    generator_match_count += 1
                    self.assertIsInstance(d_point["port_route"], list)
                    self.assertIn(data.PORT_TANG, list(d_point["port_route"]))
                    self.assertEqual(list(data.get_data()[i]["port_route"])[:1], [data.PORT_TANG])
                    results.append(d_point)
                search.consumable_iterators = None
            elif search(d_point):
                results.append(d_point)
        assert results
        assert generator_match_count


class TestWhere(Base.SearchMixin, Base.ExceptionsMixin):
    exceptions = [
        (lambda: DictSearch({"port_route": {"$where": {1, 2}}}), exceptions.ArraySelectorFormatException),
    ]

    def setUp(self) -> None:
        super().setUp()
        self.search_checks = [
            (  # where eq
                DictSearch(
                    match_query={
                        "products": {"$where": [
                            {"product": data.PROD_GR},
                            [{"product": data.PROD_GR, "due_date": datetime(2022, 7, 1), "cost": 10**6}],
                        ]},
                    }
                ),
                lambda x: self.check_func_eq(x),
            ),
            (
                DictSearch(match_query={"products": {"$where": [
                    {"product": data.PROD_PC}, {"$all": {"cost": {"$lt": 50000}}}
                ]}}),
                lambda x: self.check_func(x),
            )
        ]

    @staticmethod
    def check_func_eq(x):
        found = list(filter(lambda y: y["product"] == data.PROD_GR,  x["products"]))
        if found:
            return all(r == {"product": data.PROD_GR, "due_date": datetime(2022, 7, 1), "cost": 10**6} for r in found)
        else:
            return False

    @staticmethod
    def check_func(x):
        found = list(filter(lambda y: y["product"] == data.PROD_PC,  x["products"]))
        if found:
            return all(r.get("cost", 51000) < 50000 for r in found)
        else:
            return False

    def test_implementation(self):
        search = DictSearch()
        data = [{"d": 1}, {"d": 0}, {"a": 1}, {"a": 1, "d": 0}]
        op = aop.Where({"d": 0})
        result = op(data, search)
        self.assertEqual(result, [data[1], data[3]])
