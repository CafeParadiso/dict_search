from typing import Any as TypeAny

from .bases import ArrayOperator


class All(ArrayOperator):
    name = "all"

    def implementation(self, data: TypeAny, search_value: TypeAny) -> bool:
        values = list(data)
        return False if not values else all(values)


class Any(ArrayOperator):
    name = "any"

    def implementation(self, data, search_value) -> bool:
        return any(data)
