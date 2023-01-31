import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from pprint import pprint
from types import FunctionType, MethodType
from typing import Any, Type, Union, get_type_hints, final

from . import exceptions


@dataclass
class MatchNode:
    """Interface object to expose and Operator instance to DictSearch match method

    operator: Operator instance
    query: Set if your operator should be used alongside a subquery in DictSearch.
    """
    operator: "Operator"
    query: dict = None


class Operator(ABC):
    _match_node = MatchNode
    name: str = None
    default_return: Any = None

    @abstractmethod
    def implementation(self, *args) -> Any:
        """Write your operator logic here"""
        raise NotImplementedError

    @classmethod
    def init_match_node(cls, match_query: Any, parse_func: typing.Callable) -> MatchNode:
        """Implement this method if your op will be used as a match operator

        Example:
            arg_1, arg_2 = match_query[0], match_query[0] + 2
            return cls._match_node(cls(arg_1, arg_2))
        """

    def precondition(self, args: Any) -> Any:
        """Implement this method if you want to error check any initialization arguments

        This method should be executed on __init__ and should return values for the __init__ attributes, e.g.:

        def __init__(attr1, attr2):
            self.attr1, self.attr2 = self.precondition(attr1, attr2)
        """

    def __str__(self):
        return (
            f"{self.__class__} {self.name}\n"
            f"{self.__class__.default_return.fget.__name__}: {self.default_return}\n"
            f"{self.__class__.allowed_types.fget.__name__}: {self.allowed_types}\n"
            f"{self.__class__.ignored_types.fget.__name__}: {self.ignored_types}\n"
            f"{self.__class__.expected_exc.fget.__name__}: {self.expected_exc}\n"
        )

    def __call__(self, *args, **kwargs) -> Any:
        return self.implementation(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        for attr in ["name", "default_return"]:
            if getattr(instance, attr) is None:
                raise exceptions.OperatorImplementationMissingAttr(cls, attr)
        if not isinstance(cls.name, str):
            raise exceptions.OperatorImplementationNameError(cls, "name")
        non_overidable = [
            Operator.expected_exc.fget.__name__,
            Operator.allowed_types.fget.__name__,
            Operator.ignored_types.fget.__name__,
            Operator.__call__.__name__,
            Operator.__wrap_implementation.__name__,
        ]
        for attr_name in non_overidable:
            if attr_name in cls.__dict__:
                raise exceptions.OperatorImplementationOverrideError(attr_name)
        if not isinstance(cls.init_match_node, MethodType):
            raise exceptions.OperatorImplementationInitMatchNodeError(
                cls.__name__, Operator.init_match_node.__name__,
            )
        return instance

    def __init__(
        self,
        expected_exc: Union[Type[Exception], tuple[..., Type[Exception]], dict] = None,
        allowed_types: Union[Type, tuple[..., Type]] = None,
        ignored_types: Union[Type, tuple[..., Type]] = None,
    ):
        self.original_implementation = self.implementation
        self.__implementation_wrappers = {
            Operator.expected_exc.fget.__name__: None,
            Operator.ignored_types.fget.__name__: None,
            Operator.allowed_types.fget.__name__: None,
        }
        self.expected_exc = expected_exc
        self.ignored_types = ignored_types
        self.allowed_types = allowed_types

    @property
    def expected_exc(self):
        return self._expected_exc

    @expected_exc.setter
    def expected_exc(self, expected_exc: Union[Type[Exception], tuple[..., Type[Exception]]]):
        func_name = Operator.expected_exc.fget.__name__
        is_exc = lambda x: isinstance(x, type) and issubclass(x, Exception)
        is_type_ok = lambda x: all(isinstance(v, type(self.default_return)) for v in x)
        if expected_exc is None:
            self._expected_exc = None
        elif is_exc(expected_exc):
            self._expected_exc = {expected_exc: self.default_return}
        elif isinstance(expected_exc, tuple) and all(map(is_exc, expected_exc)):
            self._expected_exc = {exc: self.default_return for exc in expected_exc}
        elif isinstance(expected_exc, dict) and all(map(is_exc, expected_exc)) and is_type_ok(expected_exc.values()):
            self._expected_exc = expected_exc
        else:
            raise exceptions.OperatorExpectedExcArgError(func_name, type(self.default_return))
        self.__implementation_wrappers[func_name] = None if not expected_exc else self.__expected_exc
        self.__wrap_implementation()

    def __expected_exc(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except tuple(self.expected_exc.keys()) as e:
            exc_type = type(e)
            if exc_type in self.expected_exc:
                return self.expected_exc[exc_type]
            parent_exc_type = list(filter(lambda x: x in self.expected_exc, e.__class__.mro()))[0]  # first in mro order
            return self.expected_exc[parent_exc_type]

    def __set_type_checkers(self, val, func_name, func):
        if val and not(isinstance(val, type) or (isinstance(val, tuple) and all(isinstance(v, type) for v in val))):
            raise exceptions.OperatorTypeCheckerError(func_name)
        setattr(self, f"_{func_name}", val)
        self.__implementation_wrappers[func_name] = func if val else None
        self.__wrap_implementation()

    @property
    def ignored_types(self):
        return self._ignored_types

    @ignored_types.setter
    def ignored_types(self, value):
        self.__set_type_checkers(value, Operator.ignored_types.fget.__name__, self.__ignored_types)

    def __ignored_types(self, func, data, *args):
        if isinstance(data, self.ignored_types):
            return self.default_return
        return func(data, *args)

    @property
    def allowed_types(self):
        return self._allowed_types

    @allowed_types.setter
    def allowed_types(self, value):
        self.__set_type_checkers(value, Operator.allowed_types.fget.__name__, self.__allowed_types)

    def __allowed_types(self, func, data, *args):
        if not isinstance(data, self.allowed_types):
            return self.default_return
        return func(data, *args)

    def __wrap_implementation(self):
        self.implementation = self.original_implementation
        for func in filter(lambda x: x is not None, self.__implementation_wrappers.values()):
            self.implementation = partial(func, self.implementation)


class LowLevelOperator(Operator, ABC):
    default_return = False

    @classmethod
    def init_match_node(cls, match_query, *args) -> MatchNode:
        return cls._match_node(cls(match_query))


class HighLevelOperator(Operator, ABC):
    default_return = False

    @classmethod
    def init_match_node(cls, match_query, parse_func) -> MatchNode:
        if not isinstance(match_query, list) or not match_query:
            raise exceptions.HighLevelOperatorIteratorError(list, list)
        return cls._match_node(cls(), [parse_func(v) for v in match_query])


class ArrayOperator(Operator, ABC):
    default_return = False

    @classmethod
    def init_match_node(cls, match_query, parse_func) -> MatchNode:
        match_query = parse_func(match_query) if isinstance(match_query, dict) else match_query
        return cls._match_node(cls(True), match_query)


class ArraySelector(Operator, ABC):
    default_return = []

    @classmethod
    def init_match_node(cls, match_query, parse_func) -> MatchNode:
        if not isinstance(match_query, list) or len(match_query) != 2:
            raise exceptions.ArraySelectorFormatException(f"{cls.name}")
        init_arg, match_query = match_query
        match_query = parse_func(match_query) if isinstance(match_query, dict) else match_query
        return cls._match_node(cls(init_arg), match_query)


class ShortcircuitMixin(ABC):
    @staticmethod
    def shortcircuit_counter(generator, thresh, check, eager_check, eager_value):
        count = 0
        for match in generator:
            if match:
                count += 1
                if eager_check(count, thresh):
                    return eager_value
        return check(count, thresh)


class MatchOperator(HighLevelOperator, Operator, ShortcircuitMixin, ABC):
    def __init__(self, thresh, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresh = self.precondition(thresh)

    def precondition(self, thresh: Any):
        if not isinstance(thresh, int):
            raise exceptions.MatchOperatorError(self.name)
        return thresh

    def implementation(self, iterable) -> bool:
        return self.shortcircuit_counter(iterable, self.thresh, *self.shortcircuit_args())

    @abstractmethod
    def shortcircuit_args(self):
        f"""Arguments needed by '{self.shortcircuit_counter.__name__}' determined by the operator"""

    @classmethod
    def init_match_node(cls, match_query, parse_func) -> MatchNode:
        if not isinstance(match_query, dict) or not match_query:
            raise exceptions.MatchOperatorError(cls.name)
        thresh, sub_query = list(match_query.items())[0]
        if not isinstance(sub_query, list):
            raise exceptions.HighLevelOperatorIteratorError(list, sub_query)
        return cls._match_node(cls(thresh), [parse_func(v) for v in sub_query])


class CountOperator(ArrayOperator, ShortcircuitMixin, ABC):
    def __init__(self, thresh, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresh = self.precondition(thresh)

    def precondition(self, thresh: Any):
        if not isinstance(thresh, int):
            raise exceptions.MatchOperatorError(self.name)
        return thresh

    def implementation(self, data) -> Any:
        return self.shortcircuit_counter(data, self.thresh, *self.shortcircuit_args())

    @abstractmethod
    def shortcircuit_args(self):
        f"""Arguments needed by '{self.shortcircuit_counter.__name__}' determined by the operator"""

    @classmethod
    def init_match_node(cls, match_query, parse_func) -> MatchNode:
        if not isinstance(match_query, dict):
            raise Exception
        thresh, match_query = list(match_query.items())[0]
        match_query = parse_func(match_query) if isinstance(match_query, dict) else match_query
        return cls._match_node(cls(thresh), match_query)
