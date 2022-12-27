from typing import Any as TypeAny

from src.dict_search.operators.bases import ArrayOperator


class All(ArrayOperator):
    name = "all"

    def implementation(self, data: TypeAny, search_value: TypeAny) -> bool:
        return False if not data else all(v == search_value for v in data)


class Any(ArrayOperator):
    name = "any"

    def implementation(self, data, search_value) -> bool:
        return any(v == search_value for v in data)
