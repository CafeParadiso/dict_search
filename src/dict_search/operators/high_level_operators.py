from .bases import HighLevelOperator, MatchOperator

from typing import Any


class And(HighLevelOperator):
    name = "and"

    def implementation(self, data, match_query, prev_keys) -> bool:
        matches = super().implementation(data, match_query, prev_keys)
        return all(matches)


class Or(HighLevelOperator):
    name = "or"

    def implementation(self, data, match_query, prev_keys) -> bool:
        matches = super().implementation(data, match_query, prev_keys)
        return any(matches)


class Not(HighLevelOperator):
    name = "not"

    def implementation(self, data, match_query, prev_keys) -> bool:
        matches = super().implementation(data, match_query, prev_keys)
        return not all(matches)


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
