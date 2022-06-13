from . import constants


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


def shortcircuit_counter(generator, check, counter, eager_check, eager_value):
    matches = 0
    for match in generator:
        if match:
            matches += 1
            if eager_check(matches, counter):
                return eager_value
    return check(matches, counter)


def set_from_list(dikt, keys, val):
    if len(keys) == 1:
        dikt[keys[0]] = val
        return dikt
    key = keys[0]
    dikt[key] = {} if key not in dikt.keys() else dikt[key]
    set_from_list(dikt[key], keys[1:], val)


def pop_from_list(dikt, keys):
    if len(keys) == 1:
        dikt.pop(keys[0], None)
        return dikt
    key = keys[0]
    pop_from_list(dikt[key], keys[1:])
