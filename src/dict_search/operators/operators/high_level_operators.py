from ..bases import HighLevelOperator


class And(HighLevelOperator):
    name = "and"

    def implementation(self, data) -> bool:
        return all(data)


class Or(HighLevelOperator):
    name = "or"

    def implementation(self, data) -> bool:
        return any(data)


class Not(HighLevelOperator):
    name = "not"

    def implementation(self, data) -> bool:
        return not all(data)
