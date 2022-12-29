# import types
# from collections import abc
# from pprint import pprint
#
# from pytest import raises as pytest_raises
#
# from src.dict_search.dict_search import DictSearch
# from src.dict_search.operators import exceptions
# from test.fixtures import data
#
#
# def test_index_malformed():
#     with pytest_raises(exceptions.IndexOperatorError):
#         for d_point in data.read_fixtures():
#             DictSearch(select_query={"batch": {"products": {"$index": 1}}})(d_point)
#
#
# def test_index_nested_missing_key():
#     values = list(
#         filter(
#             lambda x: x is not None,
#             iter(
#                 DictSearch(select_query={"batch": {"products": {"$index": {4: {"missing": 1}}}}})(d)
#                 for d in data.read_fixtures()
#             ),
#         )
#     )
#     assert not values
#
#
# def test_index_include():
#     counter = 0
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         values = DictSearch(select_query={"batch": {"products": {"$index": {6: 1}}}})(d_point)
#         if values:
#             counter += 1
#             assert d_point == original_data
#             assert values == {"batch": {"products": d_point["batch"]["products"][6]}}
#     assert counter == 6
#
#
# def test_index_multiple():
#     d = [
#         {"b": "demo", "a": ({"b": 2, "c": 1}, 2, {"b": 4}, {"b": 5})},
#         {"a": 1},
#         {"a": [{"b": 2, "c": 2}, {"b": 3}, {"b": 4}, {"b": 5}]},
#         {"a": {"b": 1}, "b": 4},
#         {"a": {"b": {1, "b", 3, 4, 5}}},
#         {"b": "1234"},
#         {"a": "1234", "b": 1},
#     ]
#     for d_point in d:
#         values = DictSearch(select_query={"a": {"$index": [[0, -1], {"b": 1}]}, "b": 1}, coerce_list=True)(d_point)
#         if values:
#             pprint(values)
#
#
# def test_index_include_nested():
#     counter = 0
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         values = DictSearch(select_query={"batch": {"products": {"$index": {4: {"product": 1}}}}})(d_point)
#         if values is not None:
#             counter += 1
#             assert d_point == original_data
#             assert values == {"batch": {"products": {"product": d_point["batch"]["products"][4]["product"]}}}
#     assert counter == 6
#
#
# def test_index_include_generator():
#     counter = 0
#     for i, d_point in enumerate(data.read_fixtures()):
#         assert isinstance(d_point["port_route"], types.GeneratorType)
#         values = DictSearch(consumable_iterators=abc.Iterator, select_query={"port_route": {"$index": {0: 1}}})(d_point)
#         assert isinstance(d_point["port_route"], list)  # assert generator has been transformed
#         assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])  # same values as original
#         if values:
#             counter += 1
#             assert values == {"port_route": d_point["port_route"][0]}
#     assert counter == 8
#
#
# def test_index_include_nested_generator():
#     counter = 0
#     for i, d_point in enumerate(data.read_fixtures()):
#         assert isinstance(d_point["port_route"], types.GeneratorType)
#         value = DictSearch(
#             consumable_iterators=abc.Iterator, select_query={"port_route": {"$index": {0: {"days": 1}}}}
#         )(d_point)
#         assert isinstance(d_point["port_route"], list)
#         assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
#         if value:
#             counter += 1
#             assert value == {"port_route": {"days": d_point["port_route"][0]["days"]}}
#     assert counter == 7
#
#
# def test_index_exclude():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$index": {0: 0}}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         value = search(d_point)
#         if value:
#             counter += 1
#             assert d_point == original_data
#             d_point["batch"]["products"].pop(0)
#             assert value == d_point
#     assert counter == 10
#
#
# def test_index_exclude_nested():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$index": {0: {"product": 0}}}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         value = search(d_point)
#         if value:
#             counter += 1
#             assert d_point == original_data
#             d_point["batch"]["products"][0].pop("product")
#             assert value == d_point
#     assert counter == 10
#
#
# def test_index_exclude_generator():
#     counter = 0
#     search = DictSearch(select_query={"port_route": {"$index": {0: 0}}}, consumable_iterators=abc.Iterator)
#     for i, d_point in enumerate(data.read_fixtures()):
#         assert isinstance(d_point["port_route"], types.GeneratorType)
#         value = search(d_point)
#         assert isinstance(d_point["port_route"], list)
#         assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
#         if value:
#             counter += 1
#             d_point["port_route"].pop(0)
#             assert value == d_point
#     assert counter == 8
#
#
# def test_index_exclude_nested_generator():
#     counter = 0
#     search = DictSearch(consumable_iterators=abc.Iterator, select_query={"port_route": {"$index": {0: {"port": 0}}}})
#     for i, d_point in enumerate(data.read_fixtures()):
#         assert isinstance(d_point["port_route"], types.GeneratorType)
#         value = search(d_point)
#         assert isinstance(d_point["port_route"], list)
#         assert d_point["port_route"] == list(list(data.read_fixtures())[i]["port_route"])
#         if value:
#             counter += 1
#             d_point["port_route"][0].pop("port")
#             assert value == d_point
#     assert counter == 7
#
#
# def test_slice_malformed():
#     with pytest_raises(exceptions.ArraySelectorFormatException):
#         for d_point in data.read_fixtures():
#             DictSearch(select_query={"batch": {"products": {"$slice": {complex(2, 3): 0}}}})(d_point)
#
#
# def test_slice_include():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$slice": {":2": 1}}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         value = search(d_point)
#         if value:
#             counter += 1
#             assert d_point == original_data
#             assert value == {"batch": {"products": d_point["batch"]["products"][:2]}}
#     assert counter == 10
#
#
# def test_slice_include_nested():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$slice": {":2": {"product": 1}}}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         values = search(d_point)
#         if values:
#             counter += 1
#             assert d_point == original_data
#             assert values == {
#                 "batch": {"products": [{"product": p["product"]} for p in d_point["batch"]["products"][:2]]}
#             }
#     assert counter == 10
#
#
# def test_slice_exclude():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$slice": {"2:": 0}}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         values = search(d_point)
#         if values:
#             counter += 1
#             assert d_point == original_data
#             del d_point["batch"]["products"][2:]
#             assert values == d_point
#
#
# def test_slice_exclude_nested():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$slice": {"2:": {"product": 0}}}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         values = search(d_point)
#         if values:
#             counter += 1
#             assert d_point == original_data
#             [val.pop("product") for val in d_point["batch"]["products"][2:]]
#             assert values == d_point
#
#
# def test_where_malformed():
#     with pytest_raises(exceptions.WhereOperatorError):
#         for d_point in data.read_fixtures():
#             DictSearch(select_query={"batch": {"products": {"$where": {"product": "Iron"}}}})(d_point)
#
#
# def test_where_included():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$where": [{"product": "Iron"}, 1]}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         value = search(d_point)
#         if value:
#             pprint(value)
#             counter += 1
#             assert d_point == original_data
#             assert value == {
#                 "batch": {"products": [dp for dp in d_point["batch"]["products"] if dp["product"] == "Iron"]}
#             }
#     assert counter == 3
#
#
# def test_where_included_nested():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$where": [{"product": "Iron"}, {"due": 1}]}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         values = search(d_point)
#         if values:
#             assert d_point == original_data
#             assert values == {
#                 "batch": {
#                     "products": [
#                         {"due": dp["due"]}
#                         for dp in list(
#                             filter(
#                                 lambda x: True if x.get("due") and x["product"] == "Iron" else False,
#                                 d_point["batch"]["products"],
#                             )
#                         )
#                     ]
#                 }
#             }
#             counter += 1
#     assert counter == 1
#
#
# def test_where_excluded():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$where": [{"product": "Iron"}, 0]}}})
#     for d_point in data.read_fixtures():
#         original_data = d_point.copy()
#         value = search(d_point)
#         if value:
#             counter += 1
#             assert d_point == original_data
#             d_point["batch"]["products"] = [dp for dp in d_point["batch"]["products"] if dp["product"] != "Iron"]
#             assert value == d_point
#     assert counter == 3
#
#
# def test_where_excluded_nested():
#     counter = 0
#     search = DictSearch(select_query={"batch": {"products": {"$where": [{"product": "Iron"}, {"due": 0}]}}})
#     for d_point in data.read_fixtures():
#         print(d_point["batch"]["products"])
#         original_data = d_point.copy()
#         value = search(d_point)
#         if value:
#             assert d_point == original_data
#             d_point["batch"]["products"] = list(
#                 filter(
#                     lambda x: True if x.get("due") and x["product"] == "Iron" else False, d_point["batch"]["products"]
#                 )
#             )
#             for dp in d_point["batch"]["products"]:
#                 dp.pop("due")
#             assert value == d_point
#             counter += 1
#     assert counter == 1
