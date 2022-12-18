from typing import Iterable


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


def greedy_search(dikt, keys, max_depth=10, candidates=1, index=None, iterables=None):
    if not keys:
        raise Exception("argument keys cannot be empty")
    keys = [keys] if not isinstance(keys, list) else keys
    results = []
    for result in __recursive_greedy_serch(dikt, keys, max_depth=max_depth, iterables=iterables):
        results.append(result)
        if len(results) == candidates:
            return results if index is None else __try_index(results, index)
    return results if index is None else __try_index(results, index)


def __recursive_greedy_serch(
    obj: dict,
    keys: list,
    found_keys: list = None,
    initial_keys: list = None,
    depth: int = 0,
    max_depth: int = 10,
    iterables: Iterable = None,
):
    found_keys = [] if not found_keys else found_keys
    initial_keys = keys if not initial_keys else initial_keys
    if found_keys == initial_keys:
        yield obj
    if isinstance(obj, dict) and keys and depth <= max_depth:
        for key, value in obj.items():
            if key == keys[0]:
                found_keys.append(key)
                depth += 1
                yield from __recursive_greedy_serch(
                    value, keys[1:], found_keys, initial_keys, depth, max_depth, iterables
                )
                found_keys.pop()
                depth -= 1
            else:
                depth += 1
                yield from __recursive_greedy_serch(value, keys, found_keys, initial_keys, depth, max_depth, iterables)
                depth -= 1
    elif iterables and isinstance(obj, iterables):
        for sub_obj in obj:
            depth += 1
            yield from __recursive_greedy_serch(sub_obj, keys, found_keys, initial_keys, depth, max_depth, iterables)
            depth -= 1


def __try_index(lst: list, index: int):
    if len(lst) - 1 >= index:
        return lst[index]
    while index >= len(lst):
        index = index - 1
    if lst:
        return lst[index]
    return lst
