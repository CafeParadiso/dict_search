import logging
from abc import ABC, abstractmethod
from functools import partial, cache, lru_cache
from types import FunctionType
from typing import Any, Type, Union

from src.dict_search.operators import exceptions
from src.dict_search import Operator

from test.utils import TestCase


class OperatorWrapper(ABC):
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
    def implementation(self, data, *args, **kwargs) -> Any:  # pragma: no cover
        """Write your operator logic here."""
        raise NotImplementedError

    def log(self, result: Any) -> None:
        """Logs the result of your implementation function at info level, overwrite the method if needed."""
        logging.info(f"{result}")

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    # def __call__(self, data, *args, **kwargs) -> Any:
    #     # logging.debug(f"{self.name}")
    #     # result = self.implementation(data, *args, **kwargs)
    #     # self.log(result)
    #     # return result
    #     return self.implementation(data, *args, **kwargs)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        base_classes = {cl for cl in cls.__mro__ if cl not in [OperatorWrapper, ABC, object]}
        implemented_attrs = set(
            key for cl in base_classes for key in cl.__dict__.keys() if not any(key.startswith(s) for s in ["_", "__"])
        )
        class_attrs = {Operator.name.fget.__name__, Operator.initial_default_return.fget.__name__}
        overridable_attrs = {Operator.implementation.__name__, Operator.log.__name__}
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
        #self.__original_implementation = self.__class__.__call__
        self.__original_implementation = self.implementation
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

    def __expected_exc(self, func):
        def wrapper_exc(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(self.expected_exc.keys()) as e:
                exc_type = type(e)
                if exc_type in self.expected_exc:
                    return self.expected_exc[exc_type]
                return [v for k, v in self.expected_exc.items() if issubclass(exc_type, k)][0]
        return wrapper_exc

    @property
    def ignored_types(self):
        return self._ignored_types

    @ignored_types.setter
    def ignored_types(self, value):
        self.__set_type_checkers(value, Operator.ignored_types.fget.__name__, self.__ignored_types)

    def __ignored_types(self, func):
        def wrapper_ignored(data, *args):
            if isinstance(data, self.ignored_types):
                logging.info(f"Type ignored: {type(data)}")
                return self.default_return
            return func(data, *args)
        return wrapper_ignored

    @property
    def allowed_types(self):
        return self._allowed_types

    @allowed_types.setter
    def allowed_types(self, value):
        self.__set_type_checkers(value, Operator.allowed_types.fget.__name__, self.__allowed_types)

    def __allowed_types(self, func):
        def wrapper_allowed(data, *args):
            if not isinstance(data, self.allowed_types):
                return self.default_return
            return func(data, *args)
        return wrapper_allowed

    def __set_type_checkers(self, value, func_name, func):
        if value and not (
            isinstance(value, type) or isinstance(value, tuple) and all(isinstance(v, type) for v in value)
        ):
            raise exceptions.OperatoTypeCheckerError(func_name)
        setattr(self, f"_{func_name}", value)
        self.__implementation_wrappers[func_name] = func if value else None
        self.__wrap_implementation()

    def __wrap_implementation(self):
        # self.__class__.__call__ = self.__original_implementation
        # for func in filter(lambda x: x is not None, self.__implementation_wrappers.values()):
        #     self.__class__.__call__ = func(self.__class__.__call__)
        # self.__class__.__call__ = cache(self.__class__.__call__)
        self.implementation = self.__original_implementation
        for func in filter(lambda x: x is not None, self.__implementation_wrappers.values()):
            self.implementation = func(self.implementation)


class OperatorIf(ABC):
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
    def implementation(self, data, *args, **kwargs) -> Any:  # pragma: no cover
        """Write your operator logic here."""
        raise NotImplementedError

    def log(self, result: Any) -> None:
        """Logs the result of your implementation function at info level, overwrite the method if needed."""
        logging.info(f"{result}")

    def __call__(self, data, *args, **kwargs) -> Any:
        #logging.debug(f"{self.name}")
        if self.allowed_types and not isinstance(data, self.allowed_types):
            return self.default_return
        if self.ignored_types and isinstance(data, self.ignored_types):
            logging.info(f"Type ignored: {type(data)}")
            return self.default_return
        try:
            result = self.implementation(data, *args, **kwargs)
            return result
        except tuple(self.expected_exc.keys()) as e:
            exc_type = type(e)
            if exc_type in self.expected_exc:
                return self.expected_exc[exc_type]
            return [v for k, v in self.expected_exc.items() if issubclass(exc_type, k)][0]

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        base_classes = {cl for cl in cls.__mro__ if cl not in [OperatorIf, ABC, object]}
        implemented_attrs = set(
            key for cl in base_classes for key in cl.__dict__.keys() if not any(key.startswith(s) for s in ["_", "__"])
        )
        class_attrs = {Operator.name.fget.__name__, Operator.initial_default_return.fget.__name__}
        overridable_attrs = {Operator.implementation.__name__, Operator.log.__name__}
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
                logging.info(f"Type ignored: {type(data)}")
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
            raise exceptions.OperatoTypeCheckerError(func_name)
        setattr(self, f"_{func_name}", value)
        self.__implementation_wrappers[func_name] = func if value else None
        self.__wrap_implementation()

    def __wrap_implementation(self):
        pass


if __name__ == '__main__':
    import timeit
    from operator import eq as py_eq

    class Eq(Operator):
        name = "eq"
        initial_default_return = False

        def implementation(self, data, comp) -> bool:
            return data == comp

    class EqWrap(OperatorWrapper):
        name = "eq"
        initial_default_return = False

        def implementation(self, data, comp) -> bool:
            return data == comp

        def __call__(self, data, comp):
            return data == comp

    class EqIf(OperatorIf):
        name = "eq"
        initial_default_return = False

        def implementation(self, data, comp) -> bool:
            return data == comp

    # 7.5, 7.3 7.3 7.45

    eqi = EqIf(expected_exc=ValueError, ignored_types=float, allowed_types=int)
    eq = Eq(expected_exc=ValueError, ignored_types=float, allowed_types=int)
    eqw = EqWrap(ignored_types=int)
    eqw.implementation([], 2)
    eqw([], 2)
    n = 900000
    data = [2, '2', 2.2, 1, 2, 3, 1, 2, '2', []]
    q = 2

    print(f"py eq: {timeit.timeit(lambda: list(map(lambda x: py_eq(x, 2), data)), number=n)}")
    #print(f"Eq: {timeit.timeit(lambda: list(map(lambda x: eq.implementation(x, 2), data)), number=n)}")
    #print(f"Eqi: {timeit.timeit(lambda: list(map(lambda x: eqi(x, 2), data)), number=n)}")
    #print(f"Eqw: {timeit.timeit(lambda: list(map(lambda x: eqw(x, 2), data)), number=n)}")
    print(f"Eqw IMP: {timeit.timeit(lambda: list(map(lambda x: eqw.implementation(x, 2), data)), number=n)}")
    print(f"Eqw: {timeit.timeit(lambda: list(map(lambda x: eqw(x, 2), data)), number=n)}")
    print(f"==: {timeit.timeit(lambda: list(map(lambda x: x == 2, data)), number=n)}")
    eqw.expected_exc, eqw.ignored_types, eqw.allowed_types = ValueError, float, int
    print(f"Eqw: {timeit.timeit(lambda: list(map(lambda x: eqw(x, 2), data)), number=n)}")
    # print("clean")
    # eq = Eq()
    # eqw = EqWrap()
    # eqi = EqIf()
    # eq(2, 2)
    # eqw(2, 2)
    # print(f"Eq: {timeit.timeit(lambda: list(map(lambda x: eq(x, 2), data)), number=n)}")
    # print(f"Eqi: {timeit.timeit(lambda: list(map(lambda x: eqi(x, 2), data)), number=n)}")
    # print(f"Eqw: {timeit.timeit(lambda: list(map(lambda x: eqw(x, 2), data)), number=n)}")
    #
    # # print(f"==: {timeit.timeit(lambda: list(map(lambda x: x == 2, data)), number=n)}")
    # # print(f"Eqi: {timeit.timeit(lambda: list(map(lambda x: eqi(x, 2), data)), number=n)}")
    # # print(f"Eqw: {timeit.timeit(lambda: list(map(lambda x: eqw(x, 2), data)), number=n)}")
    # # print(f"Eq: {timeit.timeit(lambda: list(map(lambda x: eq(x, 2), data)), number=n)}")
    # # print(f"==: {timeit.timeit(lambda: list(map(lambda x: x == 2, data)), number=n)}")
    # # print(f"py eq: {timeit.timeit(lambda: list(map(lambda x: py_eq(x, 2), data)), number=n)}")
    # # print(f"Eq imp: {timeit.timeit(lambda: list(map(lambda x: eq.implementation(x, 2), data)), number=n)}")
    # # print(f"Eqw imp: {timeit.timeit(lambda: list(map(lambda x: eqw.implementation(x, 2), data)), number=n)}")
    # #print(f"Eqi: {timeit.timeit(lambda: list(map(lambda x: eqi(x, 2), data)), number=n)}")