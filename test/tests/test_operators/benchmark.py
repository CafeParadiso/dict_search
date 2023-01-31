import logging
from abc import ABC, abstractmethod
from functools import partial, cache, lru_cache
from types import FunctionType
from typing import Any, Type, Union

from src.dict_search.operators import exceptions
from src.dict_search import Operator

from test.utils import TestCase

if __name__ == "__main__":

    class Demo(Operator):
        """
        {"a": 123}
        """

        name = "5"
