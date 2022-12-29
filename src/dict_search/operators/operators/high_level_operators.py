from typing import Iterable

from src.dict_search.operators.bases import HighLevelOperator


class And(HighLevelOperator):
    name = "and"

    def implementation(self, data: Iterable[bool]) -> bool:
        return all(data)


class Or(HighLevelOperator):
    name = "or"

    def implementation(self, data: Iterable[bool]) -> bool:
        return any(data)


class Not(HighLevelOperator):
    name = "not"

    def implementation(self, data: Iterable[bool]) -> bool:
        return not all(data)


class NotAny(HighLevelOperator):
    name = "not_any"

    def implementation(self, data: Iterable[bool]) -> bool:
        return not any(data)
