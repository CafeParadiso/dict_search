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


def set_from_list(dikt, keys, val):
    if len(keys) == 1:
        dikt.update({keys[0]: val})
        return dikt
    try:
        prev_val = get_from_list(dikt, keys[:-1]).copy()
        prev_val.update({keys[-1]: val})
        set_from_list(dikt, keys[:-1], prev_val)
    except KeyError:
        set_from_list(dikt, keys[:-1], {keys[-1]: val})


def get_from_list(dikt, keys):
    if len(keys) == 1:
        return dikt[keys[0]]
    get_from_list(dikt[keys[0]], keys[1:])


def pop_from_list(dikt, keys):
    if not dikt:
        return
    if len(keys) == 1:
        dikt.pop(keys[0], None)
    if len(keys) == 2:
        dikt.update({keys[0]: {k: v for k, v in dikt[keys[0]].items() if k != keys[1]}})
    else:
        pop_from_list(dikt.get(keys[0]), keys[1:])
    return dikt
