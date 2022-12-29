from typing import Any as TypeAny

from src.dict_search.operators.bases import ArrayOperator


class All(ArrayOperator):
    name = "all"

    def __init__(self, search_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_value = search_value

    def implementation(self, data: TypeAny) -> bool:
        return False if not data else all(v == self.search_value for v in data)


class Any(ArrayOperator):
    name = "any"

    def __init__(self, search_value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_value = search_value

    def implementation(self, data) -> bool:
        return any(v == self.search_value for v in data)
