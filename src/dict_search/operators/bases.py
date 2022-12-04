import logging
from abc import ABC, abstractmethod
from functools import partial
from pprint import pprint
from types import FunctionType
from typing import Any, Type, Union

from . import exceptions


class Operator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        """The name of our operator. Implement as class attribute"""
        raise NotImplementedError

    @property
    @abstractmethod
    def initial_default_return(self) -> Any:  # pragma: no cover
        """Initial value for default return. Implement as class attribute"""
        raise NotImplementedError

    @abstractmethod
    def implementation(self, data, *args) -> Any:  # pragma: no cover
        """Write your operator logic here."""
        raise NotImplementedError

    def log(self, result: Any) -> None:
        """Logs the result of your implementation function at info level, overwrite the method if needed."""
        logging.info(f"{result}")

    def precondition(self, match_query: Any) -> None:
        """Implement this method if you need to verify the user input for the operator.

        This method will be executed by the search object before running the whole search.
        You should raise an exception if any precondition fails.
        """

    def __call__(self, data, *args, **kwargs) -> Any:
        # logging.debug(f"{self.name}")
        # result = self.implementation(data, *args, **kwargs)
        # self.log(result)
        # return result
        return self.implementation(data, *args, **kwargs)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        base_classes = {cl for cl in cls.__mro__ if cl not in [Operator, ABC, object]}
        implemented_attrs = set(
            key for cl in base_classes for key in cl.__dict__.keys() if not any(key.startswith(s) for s in ["_", "__"])
        )
        class_attrs = {Operator.name.fget.__name__, Operator.initial_default_return.fget.__name__}
        overridable_attrs = {Operator.implementation.__name__, Operator.log.__name__, Operator.precondition.__name__}
        implemented_attrs = implemented_attrs - overridable_attrs - class_attrs

        for attr in class_attrs:
            if isinstance(getattr(cls, attr), (property, FunctionType)):
                raise exceptions.OperatorImplementationAttrTypeError(cls, attr)
        for attr in implemented_attrs:
            if attr in Operator.__dict__:
                raise exceptions.OperatorImplementationOverrideError(attr)
        if not isinstance(cls.name, str):
            raise exceptions.OperatorImplementationNameError(cls, Operator.name.fget.__name__)
        return instance

    def __init__(
        self,
        expected_exc: Union[Type[Exception], tuple[..., Type[Exception]], dict] = None,
        allowed_types: Union[Type, tuple[..., Type]] = None,
        ignored_types: Union[Type, tuple[..., Type]] = None,
        default_return: Any = None,
    ):
        self.__implementation_wrappers = {
            Operator.expected_exc.fget.__name__: None,
            Operator.ignored_types.fget.__name__: None,
            Operator.allowed_types.fget.__name__: None,
        }
        self.default_return = default_return if default_return is not None else self.initial_default_return
        self.expected_exc = expected_exc
        self.ignored_types = ignored_types
        self.allowed_types = allowed_types

    @property
    def default_return(self):
        return self._default_return

    @default_return.setter
    def default_return(self, value):
        if not isinstance(value, type(self.initial_default_return)):
            raise exceptions.OperatorDefaultReturnError(
                Operator.default_return.fget.__name__,
                Operator.initial_default_return.fget.__name__,
                self.initial_default_return,
            )
        self._default_return = value

    @property
    def expected_exc(self):
        return self._expected_exc

    @expected_exc.setter
    def expected_exc(self, expected_exc: Union[Type[Exception], tuple[..., Type[Exception]]]):
        func_name = Operator.expected_exc.fget.__name__
        is_exc = lambda x: isinstance(x, type) and issubclass(x, Exception)
        if expected_exc is None:
            self._expected_exc = None
        elif is_exc(expected_exc):
            self._expected_exc = {expected_exc: self.initial_default_return}
        elif isinstance(expected_exc, tuple) and all(map(is_exc, expected_exc)):
            self._expected_exc = {exc: self.initial_default_return for exc in expected_exc}
        elif (
            isinstance(expected_exc, dict)
            and all(map(is_exc, expected_exc))
            and all(isinstance(v, type(self.initial_default_return)) for v in expected_exc.values())
        ):
            self._expected_exc = expected_exc
        else:
            raise exceptions.OperatorExpectedExcArgError(func_name, type(self.initial_default_return))
        self.__implementation_wrappers[func_name] = None if not expected_exc else self.__expected_exc
        self.__wrap_implementation()

    def __expected_exc(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except tuple(self.expected_exc.keys()) as e:
            exc_type = type(e)
            if exc_type in self.expected_exc:
                return self.expected_exc[exc_type]
            return [v for k, v in self.expected_exc.items() if issubclass(exc_type, k)][0]

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

    def __set_type_checkers(self, value, func_name, func):
        if value and not (
            isinstance(value, type) or isinstance(value, tuple) and all(isinstance(v, type) for v in value)
        ):
            raise exceptions.OperatoTypeCheckerError(func_name)
        setattr(self, f"_{func_name}", value)
        self.__implementation_wrappers[func_name] = func if value else None
        self.__wrap_implementation()

    def __wrap_implementation(self):
        self.implementation = partial(type(self).implementation, self)
        for func in filter(lambda x: x is not None, self.__implementation_wrappers.values()):
            self.implementation = partial(func, self.implementation)


class LowLevelOperator(Operator, ABC):
    initial_default_return = False


class HighLevelOperator(Operator, ABC):
    initial_default_return = False

    def precondition(self, search_container):
        if not isinstance(search_container, list) or not search_container:
            raise exceptions.HighLevelOperatorIteratorError(list, list)


class ArrayOperator(Operator, ABC):
    initial_default_return = False


class ArraySelector(Operator, ABC):
    initial_default_return = []

    def precondition(self, value):
        if not isinstance(value, list):
            raise exceptions.ArraySelectorFormatException(f"{self.name}")


class ShortcircuitMixin(ABC):
    @staticmethod
    def shortcircuit_counter(thresh, generator, check, eager_check, eager_value):
        count = 0
        for match in generator:
            if match:
                count += 1
                if eager_check(count, thresh):
                    return eager_value
        return check(count, thresh)

    def precondition(self, value: Any):
        if not isinstance(value, dict) or not value:
            raise exceptions.MatchOperatorError(self.name)
        thresh, search_container = list(value.items())[0]
        if not isinstance(thresh, int):
            raise exceptions.MatchOperatorError(self.name)
        return thresh, search_container


class MatchOperator(HighLevelOperator, Operator, ShortcircuitMixin, ABC):
    def precondition(self, value):
        thresh, search_container = ShortcircuitMixin.precondition(self, value)
        super().precondition(search_container)
        if len(search_container) < thresh:
            raise exceptions.MatchOperatorCountMismatch(thresh, search_container)

    def implementation(self, iterable, thresh) -> bool:
        return self.shortcircuit_counter(thresh, iterable, *self.shortcircuit_args())

    @abstractmethod
    def shortcircuit_args(self):
        f"""Arguments needed by '{self.shortcircuit_counter.__name__}' determined by the operator"""


class CountOperator(ArrayOperator, ShortcircuitMixin, ABC):
    def implementation(self, thresh, data) -> Any:
        return self.shortcircuit_counter(thresh, data, *self.shortcircuit_args())

    @abstractmethod
    def shortcircuit_args(self):
        f"""Arguments needed by '{self.shortcircuit_counter.__name__}' determined by the operator"""

    def precondition(self, value: Any):
        super().precondition(value)
        ShortcircuitMixin.precondition(self, value)
