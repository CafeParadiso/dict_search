from abc import ABC, abstractmethod
from functools import partial
from pprint import pprint
from types import FunctionType
from typing import Any, Type, Union


class Operator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of our operator. Implement as class attribute"""
        raise NotImplementedError

    @property
    @abstractmethod
    def initial_default_return(self) -> Any:
        """Initial value for default return. Implement as class attribute"""
        raise NotImplementedError

    @abstractmethod
    def implementation(self, data, *args) -> Any:
        """Write your operator logic here."""
        raise NotImplementedError

    def precondition(self, match_query: Any) -> None:
        """Implement this method if you need to verify the user input for the operator.

        This method will be executed by the search object before running the whole search.
        You should raise an exception if any precondition fails.
        """

    def __str__(self):
        return (
            f"{self.name}\n"
            f"{self.default_return.fget.__name__}: {self.default_return}\n"
            f"{self.allowed_types.fget.__name__}: {self.allowed_types}\n"
            f"{self.ignored_types.fget.__name__}: {self.ignored_types}\n"
            f"{self.expected_exc.fget.__name__}: {self.expected_exc}\n"
        )

    def __call__(self, data, *args, **kwargs) -> Any:
        return self.implementation(data, *args, **kwargs)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        base_classes = {cl for cl in cls.__mro__ if cl not in [Operator, ABC, object]}
        implemented_attrs = set(
            key for cl in base_classes for key in cl.__dict__.keys() if not any(key.startswith(s) for s in ["_", "__"])
        )
        class_attrs = {Operator.name.fget.__name__, Operator.initial_default_return.fget.__name__}
        overridable_attrs = {Operator.implementation.__name__, Operator.precondition.__name__}
        implemented_attrs = implemented_attrs - overridable_attrs - class_attrs

        for attr in class_attrs:
            if isinstance(getattr(cls, attr), (property, FunctionType)):
                raise Exception
        for attr in implemented_attrs:
            if attr in Operator.__dict__:
                raise Exception
        if not isinstance(cls.name, str):
            raise Exception
        return instance

    def __init__(
        self,
        expected_exc: Union[Type[Exception], tuple[..., Type[Exception]], dict] = None,
        allowed_types: Union[Type, tuple[..., Type]] = None,
        ignored_types: Union[Type, tuple[..., Type]] = None,
        default_return: Any = None,
    ):
        self.original_implementation = self.implementation
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
            raise Exception
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
            raise Exception
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
            raise Exception
        setattr(self, f"_{func_name}", value)
        self.__implementation_wrappers[func_name] = func if value else None
        self.__wrap_implementation()

    def __wrap_implementation(self):
        self.implementation = self.original_implementation
        for func in filter(lambda x: x is not None, self.__implementation_wrappers.values()):
            self.implementation = partial(func, self.implementation)


class OperatorWrap(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of our operator. Implement as class attribute"""
        raise NotImplementedError

    @property
    @abstractmethod
    def initial_default_return(self) -> Any:
        """Initial value for default return. Implement as class attribute"""
        raise NotImplementedError

    @abstractmethod
    def implementation(self, data, *args) -> Any:
        """Write your operator logic here."""
        raise NotImplementedError

    def precondition(self, match_query: Any) -> None:
        """Implement this method if you need to verify the user input for the operator.

        This method will be executed by the search object before running the whole search.
        You should raise an exception if any precondition fails.
        """

    def __str__(self):
        return (
            f"{self.name}\n"
            f"{self.default_return.fget.__name__}: {self.default_return}\n"
            f"{self.allowed_types.fget.__name__}: {self.allowed_types}\n"
            f"{self.ignored_types.fget.__name__}: {self.ignored_types}\n"
            f"{self.expected_exc.fget.__name__}: {self.expected_exc}\n"
        )

    def __call__(self, data, *args, **kwargs) -> Any:
        return self.implementation(data, *args, **kwargs)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        base_classes = {cl for cl in cls.__mro__ if cl not in [OperatorWrap, ABC, object]}
        implemented_attrs = set(
            key for cl in base_classes for key in cl.__dict__.keys() if not any(key.startswith(s) for s in ["_", "__"])
        )
        class_attrs = {Operator.name.fget.__name__, Operator.initial_default_return.fget.__name__}
        overridable_attrs = {Operator.implementation.__name__, Operator.precondition.__name__}
        implemented_attrs = implemented_attrs - overridable_attrs - class_attrs

        for attr in class_attrs:
            if isinstance(getattr(cls, attr), (property, FunctionType)):
                raise Exception
        for attr in implemented_attrs:
            if attr in OperatorWrap.__dict__:
                raise Exception
        if not isinstance(cls.name, str):
            raise Exception
        return instance

    def __init__(
        self,
        expected_exc: Union[Type[Exception], tuple[..., Type[Exception]], dict] = None,
        allowed_types: Union[Type, tuple[..., Type]] = None,
        ignored_types: Union[Type, tuple[..., Type]] = None,
        default_return: Any = None,
    ):
        self.original_implementation = self.implementation
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
            raise Exception
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
            raise Exception
        self.__implementation_wrappers[func_name] = None if not expected_exc else self.__expected_exc
        self.__wrap_implementation()

    def __expected_exc(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(self.expected_exc.keys()) as e:
                exc_type = type(e)
                if exc_type in self.expected_exc:
                    return self.expected_exc[exc_type]
                return [v for k, v in self.expected_exc.items() if issubclass(exc_type, k)][0]

        return wrapper

    @property
    def ignored_types(self):
        return self._ignored_types

    @ignored_types.setter
    def ignored_types(self, value):
        self.__set_type_checkers(value, Operator.ignored_types.fget.__name__, self.__ignored_types)

    def __ignored_types(self, func):
        def wrapper(data, *args):
            if isinstance(data, self.ignored_types):
                return self.default_return
            return func(data, *args)

        return wrapper

    @property
    def allowed_types(self):
        return self._allowed_types

    @allowed_types.setter
    def allowed_types(self, value):
        self.__set_type_checkers(value, Operator.allowed_types.fget.__name__, self.__allowed_types)

    def __allowed_types(self, func):
        def wrapper(data, *args):
            if not isinstance(data, self.allowed_types):
                return self.default_return
            return func(data, *args)

        return wrapper

    def __set_type_checkers(self, value, func_name, func):
        if value and not (
            isinstance(value, type) or isinstance(value, tuple) and all(isinstance(v, type) for v in value)
        ):
            raise Exception
        setattr(self, f"_{func_name}", value)
        self.__implementation_wrappers[func_name] = func if value else None
        self.__wrap_implementation()

    def __wrap_implementation(self):
        self.implementation = self.original_implementation
        for func in filter(lambda x: x is not None, self.__implementation_wrappers.values()):
            self.implementation = func(self.implementation)


if __name__ == "__main__":
    import timeit

    class EqWrap(OperatorWrap):
        name = "eq"
        initial_default_return = False

        def implementation(self, data, val) -> Any:
            return data == val

    class EqPartial(Operator):
        initial_default_return = False
        name = "eq"

        def implementation(self, data, val) -> Any:
            return data == val

    eq_wrap = EqWrap()
    eq_partial = EqPartial()
    eq_wrap(1, 1)
    n = 50000
    data = [2, "2", 2.2, 1, 2, 3, 1, 2, "2", [], "tt", 3, 6]

    # print(f"WC: {timeit.timeit(lambda: list(map(lambda x: eq_wrap(x, 2), data)), number=n)}")
    import statistics

    wi = []
    pi = []
    for _ in range(100):
        wi.append(timeit.timeit(lambda: list(map(lambda x: eq_wrap.implementation(x, 2), data)), number=n))
        pi.append(timeit.timeit(lambda: list(map(lambda x: eq_partial.implementation(x, 2), data)), number=n))
        pi.append(timeit.timeit(lambda: list(map(lambda x: eq_partial.implementation(x, 2), data)), number=n))
        wi.append(timeit.timeit(lambda: list(map(lambda x: eq_wrap.implementation(x, 2), data)), number=n))
    print(f"WI: {statistics.mean(wi)}")
    print(f"PI: {statistics.mean(pi)}")
