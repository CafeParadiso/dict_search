from typing import Any as TypeAny

from .bases import ArrayOperator, CountOperator


class All(ArrayOperator):
    name = "all"

    def implementation(self, data: TypeAny, search_value: TypeAny, prev_keys: list[str]) -> bool:
        values = [
            match for d_point in data for match in self.search_instance._apply_match(d_point, search_value, prev_keys)
        ]
        return False if not values else all(values)


class Any(ArrayOperator):
    name = "any"

    def implementation(self, data, search_value, prev_keys) -> bool:
        return any(
            match for d_point in data for match in self.search_instance._apply_match(d_point, search_value, prev_keys)
        )


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
