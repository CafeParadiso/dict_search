from .bases import MatchOperator


class Match(MatchOperator):
    name = "match"

    def shortcircuit_args(self):
        return lambda c, t: True if c == t else False, lambda c, t: True if c > t else False, False


class Matchgt(MatchOperator):
    name = "matchgt"

    def shortcircuit_args(self):
        return lambda c, t: True if c > t else False, lambda c, t: True if c > t else False, True


class Matchgte(MatchOperator):
    name = "matchgte"

    def shortcircuit_args(self):
        return lambda c, t: True if c >= t else False, lambda c, t: True if c >= t else False, True


class Matchlt(MatchOperator):
    name = "matchlt"

    def shortcircuit_args(self):
        return lambda c, t: True if c < t else False, lambda c, t: True if c >= t else False, False


class Matchlte(MatchOperator):
    name = "matchlte"

    def shortcircuit_args(self):
        return lambda c, t: True if c <= t else False, lambda c, t: True if c > t else False, False
