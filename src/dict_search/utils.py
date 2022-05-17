from collections import abc


def isiter(data):
    try:
        iter(data)
        return True
    except TypeError:
        return False


def iscontainer(data):
    if isinstance(data, (abc.Container, abc.Generator)) and not isinstance(data, abc.Mapping):
        return True
    return False


def shortcircuit_counter(generator, check, counter, eager_check, eager_value):
    matches = 0
    for match in generator:
        if match:
            matches += 1
            if eager_check(matches, counter):
                return eager_value
    return check(matches, counter)


def compare(data, search_value):
    """Some objects like numpy.Series will raise ValueError when evaluated for truth"""
    try:
        return data == search_value
    except ValueError:
        return False


def set_from_list(dikt, keys, val):
    """recursively traverse list of keys, create nested dict (dikt) and set val"""
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
