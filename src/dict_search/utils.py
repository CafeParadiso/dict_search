from . import constants
from pprint import pprint


def isiter(data):
    try:
        iter(data)
        return True
    except TypeError:
        return False


def isoperator(data):
    if isinstance(data, (list, tuple, set)):
        return True
    return False


def israngestr(range_str):
    if not constants.RANGE_PATTERN.match(range_str):
        return False
    return True


def shortcircuit_counter(generator, check, tresh, eager_check, eager_value):
    count = 0
    for match in generator:
        if match:
            count += 1
            if eager_check(count, tresh):
                return eager_value
    return check(count, tresh)


def get_from_list(dikt, keys):
    if not isinstance(dikt, dict) or not dikt:
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
