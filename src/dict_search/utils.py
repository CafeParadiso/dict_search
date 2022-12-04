from collections.abc import Mapping


# def get_from_list(dikt, keys):
#     if isinstance(keys[0], list) and len(keys[0]) == 1 and not isinstance(dikt, Mapping):
#         try:
#             dikt = dikt[keys[0][0]]
#         except Exception:
#             raise KeyError
#     elif isinstance(dikt, Mapping) and dikt:
#         dikt = dikt[keys[0]]
#     else:
#         raise KeyError
#     if len(keys) == 1:
#         return dikt
#     return get_from_list(dikt, keys[1:])


def get_from_list(dikt, keys):
    if isinstance(dikt, dict) and not dikt:
        raise KeyError
    if len(keys) == 1:
        return dikt[keys[0]]
    return get_from_list(dikt[keys[0]], keys[1:])


def set_from_list(dikt, keys, val):
    if len(keys) == 1:
        dikt.update({keys[0]: val})
        return dikt
    try:
        prev_val = get_from_list(dikt, keys[:-1])
    except KeyError:
        return set_from_list(dikt, keys[:-1], {keys[-1]: val})
    else:
        if isinstance(prev_val, dict):
            prev_val = prev_val.copy()
            prev_val.update({keys[-1]: val})
            return set_from_list(dikt, keys[:-1], prev_val)
        else:
            return set_from_list(dikt, keys[:-1], {keys[-1]: val})


def pop_from_list(dikt, keys):
    if len(keys) == 1:
        dikt.pop(keys[0], None)
        return dikt
    try:
        prev_val = get_from_list(dikt, keys[:-1])
    except KeyError:
        return
    if not isinstance(prev_val, dict) or not prev_val:
        return
    return set_from_list(dikt, keys[:-1], {k: v for k, v in prev_val.items() if k != keys[-1]})


def greedy_search(dikt, keys, max_depth=10):
    keys = [keys] if not isinstance(keys, list) else keys
    return __recursive_greedy_serch(dikt, keys, max_depth)


def __recursive_greedy_serch(
    dikt: dict,
    keys: list,
    max_depth: int,
    depth: int = 0,
    found_keys: list = None,
    initial_keys: list = None,
):
    found_keys = [] if not found_keys else found_keys
    initial_keys = keys if not initial_keys else initial_keys
    if found_keys == initial_keys:
        return dikt[found_keys[-1]]
    if depth == max_depth:
        return
    depth += 1
    if keys[0] in dikt:
        found_keys.append(keys[0])
        return __recursive_greedy_serch(dikt, keys[1:], max_depth, depth, found_keys, initial_keys)
    for v in filter(lambda x: isinstance(x, dict), dikt.values()):
        value = __recursive_greedy_serch(v, keys, max_depth, depth, found_keys, initial_keys)
        if value:
            return value


if __name__ == "__main__":
    a = {"a": {"b": 3}, "c": {"d": [0, 1, "miaw"]}}
    # a = {"a": {"b": 3}, "c": {"d": 2}}
    keys = ["d"]
    v = greedy_search(a, keys)
    print(v)
