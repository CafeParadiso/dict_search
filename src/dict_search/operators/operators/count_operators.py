from src.dict_search.operators.bases import CountOperator


class Count(CountOperator):
    name = "count"

    def shortcircuit_args(self):
        return lambda c, t: True if c == t else False, lambda c, t: True if c > t else False, False


class Countgt(CountOperator):
    name = "countgt"

    def shortcircuit_args(self):
        return lambda c, t: True if c > t else False, lambda c, t: True if c > t else False, True


class Countgte(CountOperator):
    name = "countgte"

    def shortcircuit_args(self):
        return lambda c, t: True if c >= t else False, lambda c, t: True if c >= t else False, True


class Countlt(CountOperator):
    name = "countlt"

    def shortcircuit_args(self):
        return lambda c, t: True if c < t else False, lambda c, t: True if c >= t else False, False


class Countlte(CountOperator):
    name = "countlte"

    def shortcircuit_args(self):
        return lambda c, t: True if c <= t else False, lambda c, t: True if c > t else False, False


if __name__ == '__main__':
    d = [1, 2, 3, 4]
    c = Countlte()
    c(d, 1)
