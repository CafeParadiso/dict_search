from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable

import logging
from typing import Any, Type, Union

from . import exceptions


class Operator(ABC):
    """Base class for all operators"""
    default_return: Any = None  # Set value in your specific implementation

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of our operator. Implement as class attribute"""

    def __init__(
        self,
        search_instance,
        expected_exc: dict[Type[Exception], Any] = None,
        allowed_types: Union[Type, tuple[..., Type]] = None,
        ignored_types: Union[Type, tuple[..., Type]] = None,
        default_return: Any = None
    ):
        if self.default_return is None:
            raise NotImplementedError(f"Implement 'default_return' as a class atribute")
        self.search_instance = search_instance
        self.default_return = default_return or self.default_return
        self._isdecorated_expected = False
        self.expected_exc = expected_exc
        self._isdecorated_ignored = False
        self.ignored_types = ignored_types
        self._isdecorated_allowed = False
        self.allowed_types = allowed_types

    @property
    def expected_exc(self):
        return self._expected_exc

    @expected_exc.setter
    def expected_exc(self, expected_exc: dict[Type[Exception], Any]):
        if not expected_exc:
            self._expected_exc = None
        elif isinstance(expected_exc, type) and issubclass(expected_exc, Exception):
            self._expected_exc = {expected_exc: self.default_return}
        elif isinstance(expected_exc, tuple):
            exc_dict = {}
            for v in expected_exc:
                if isinstance(v, type) and issubclass(v, Exception):
                    exc_dict[v] = self.default_return
                elif isinstance(v, dict) and all(isinstance(k, type) and issubclass(k, Exception) for k in v):
                    exc_dict.update(v)
                else:
                    raise Exception("'Expected_exc' should be configured with an tuple of 'type' and/or 'dict'")
            self._expected_exc = exc_dict
        else:
            raise Exception(
                "'Expected_exc' should be:\n-Exception\n-{exception: val}\n-tuple[..., Exception or {Excption:val}]"
            )
        if self.expected_exc and not self._isdecorated_expected:
            self.__raise_exc = self.__expected_exc_wrapper(self.__raise_exc)
            self._isdecorated_expected = True

    def __expected_exc_wrapper(self, func):
        def wrapper(exc: Exception):
            exc_type = type(exc)
            if exc_type in self.expected_exc:
                return self.expected_exc[exc_type]
            for expected_exc_type, return_val in self.expected_exc.items():
                if isinstance(exc_type, expected_exc_type):
                    return return_val
            func(exc)
        return wrapper

    @property
    def ignored_types(self):
        return self._ignored_types

    @ignored_types.setter
    def ignored_types(self, value):
        self._ignored_types = self.__validate_conf_types("allowed_types", value)
        if self._ignored_types and not self._isdecorated_ignored:
            self.implementation = self.__ignored_wrapper(self.implementation)
            self._isdecorated_ignored = True

    def __ignored_wrapper(self, func):
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
        self._allowed_types = self.__validate_conf_types("ignored_types", value)
        if self._allowed_types and not self._isdecorated_allowed:
            self.implementation = self.__allowed_wrapper(self.implementation)
            self._isdecorated_allowed = True

    def __allowed_wrapper(self, func):
        def wrapper(data, *args):
            if not isinstance(data, self.allowed_types):
                return self.default_return
            return func(data, *args)
        return wrapper

    @staticmethod
    def __validate_conf_types(attr, val):
        if val and not (isinstance(val, type) or isinstance(val, tuple) and all(isinstance(v, type) for v in val)):
            raise Exception(f"'{attr}' should be type or tuple[..., type]")
        return val

    def __call__(self, data, *args, **kwargs) -> Any:
        try:
            return self.implementation(data, *args, **kwargs)
        except Exception as e:
            return self.__raise_exc(e)

    @abstractmethod
    def implementation(self, data, *args, **kwargs) -> Any:
        """Write your operator logic here."""

    def precondition(self, match_query: Any) -> None:
        """Implement this method if you need to verify the user input for the operator.

        This method will be executed by the search object before running the whole search.
        You should raise an exception if any precondition fails.
        """

    @staticmethod
    def __raise_exc(e: Exception):
        raise e


class LowLevelOperator(Operator, ABC):
    default_return = False


class HighLevelOperator(Operator, ABC):
    default_return = False

    def implementation(self, data, match_query, prev_keys) -> Any:
        return iter(
            match for search_dict in match_query for match in self.search_instance._match(data, search_dict, prev_keys)
        )

    def precondition(self, search_container):
        if not isinstance(search_container, self.search_instance.container_type) or not search_container:
            raise exceptions.HighLevelOperatorIteratorError(self.search_instance.container_type)


class ArrayOperator(Operator, ABC):
    default_return = False

    def __call__(self, val: Any, arg: Any, prev_keys: list[str, ...]) -> bool:
        if not isinstance(val, Iterable):
            return False
        val = self.search_instance._assign_consumed_iterator(val, prev_keys)
        return super().__call__(val, arg, prev_keys)


class ArraySelector(Operator, ABC):
    default_return = [], {}

    def __call__(self, data, search_value, prev_keys) -> (Any, dict):
        data = self.search_instance._assign_consumed_iterator(data, prev_keys)
        return super().__call__(data, search_value[0], search_value[1])

    def precondition(self, value):
        if not isinstance(value, self.search_instance.container_type):
            raise exceptions.ArraySelectorFormatException(self.name)


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
            raise Exception(f"The value for '{self.name}' should be a dict {{int: {{match_dict}}}}")
        thresh, search_container = list(value.items())[0]
        if not isinstance(thresh, int):
            raise exceptions.MatchOperatorError(search_container)


class MatchOperator(HighLevelOperator, Operator, ShortcircuitMixin, ABC):
    def implementation(self, data, match_query, prev_keys) -> bool:
        thresh, search_value = list(match_query.items())[0]
        iterable = iter(
            match
            for search_dict in search_value
            for match in self.search_instance._match(data, search_dict, prev_keys)
        )
        return self.shortcircuit_counter(thresh, iterable, *self.shortcircuit_args())

    @abstractmethod
    def shortcircuit_args(self):
        f"""Arguments needed by '{self.shortcircuit_counter.__name__}' determined by the operator"""

    def precondition(self, value: Any) -> None:
        ShortcircuitMixin.precondition(self, value)
        super().precondition(list(value.values())[0])


class CountOperator(ArrayOperator, ShortcircuitMixin, ABC):
    def implementation(self, data, match_query, prev_keys) -> Any:
        thresh, search_value = list(match_query.items())[0]
        data = self.search_instance._assign_consumed_iterator(data, prev_keys)
        if isinstance(search_value, dict):  # match is being used as array operator
            iterable = iter(
                all([m for m in self.search_instance._match(data_point, search_value, prev_keys)])
                for data_point in data
            )
        else:  # match is being used as array op. to compare each value in the array
            iterable = iter(
                self.search_instance.all_match_ops[self.search_instance.op_eq](d_point, search_value)
                for d_point in data
            )
        return self.shortcircuit_counter(thresh, iterable, *self.shortcircuit_args())

    @abstractmethod
    def shortcircuit_args(self):
        f"""Arguments needed by '{self.shortcircuit_counter.__name__}' determined by the operator"""

    def precondition(self, value: Any):
        ShortcircuitMixin.precondition(self, value)

