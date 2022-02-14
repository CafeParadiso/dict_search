import copy


def deep_get(data, key_list, default=None):
    list_copy = copy.deepcopy(key_list)
    return _deep_get(data, list_copy, default)


def _deep_get(data, key_list, default):
    if not data:
        return
    if len(key_list) == 1:
        return data.get(key_list[0])
    key = key_list.pop(0)
    return deep_get(data.get(key, default), key_list)


def deep_set(data, key_list, value):
    list_copy = copy.deepcopy(key_list)
    return _deep_set(data, list_copy, value)


def _deep_set(data, key_list, value):
    if len(key_list) == 1:
        data[key_list[0]] = value
        return data
    key = key_list.pop(0)
    if key not in data.keys():
        data[key] = {}
    return _deep_set(data[key], key_list, value)


def deep_pop(data, key_list):
    data_copy = copy.deepcopy(data)
    list_copy = copy.deepcopy(key_list)
    return _deep_pop(data_copy, list_copy)


def _deep_pop(data, key_list):
    if not data:
        return
    if len(key_list) == 1:
        data.pop(key_list[0])
        return data
    data = data.get(key_list[0])
    key_list.pop(0)
    return _deep_pop(data, key_list)