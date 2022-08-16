import unittest
from .fixtures.data import read_fixtures


class TestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.data = list(read_fixtures())
