from src.dict_search import Operator
from test.utils import TestCase, DemoOpModulo
from test.new_fixtures import CursedData
from src.dict_search.operators import exceptions


class TestOperatorImplementation(TestCase):
    def test_correct_instantiation(self):
        assert DemoOpModulo(1, 2)

    def test_abstract_class_error(self):
        class DemoOp(Operator):
            pass

        with self.assertRaises(TypeError):
            DemoOp()

    def test_class_attr(self):
        for attr in ["name", "default_return"]:
            DemoOp = type(
                f"DemoOp",
                (Operator, *Operator.__bases__),
                {attr: "1", "implementation": lambda *args, **kw: False},
            )
        with self.assertRaises(exceptions.OperatorImplementationMissingAttr):
            DemoOp()

    def test_name_value_error(self):
        class DemoOp(Operator):
            name = 1
            default_return = False

            def implementation(self, *args):
                return True

        with self.assertRaises(exceptions.OperatorImplementationNameError):
            DemoOp()

    def test_non_overridable(self):
        for attr in [
            Operator.expected_exc.fget.__name__,
            Operator.allowed_types.fget.__name__,
            Operator.ignored_types.fget.__name__,
            Operator.__call__.__name__,
            "__wrap_implementation",
        ]:
            DemoOp = type(
                f"DemoOp",
                (Operator, *Operator.__bases__),
                {
                    attr: "fail",
                    "name": "demo",
                    "implementation": lambda *args, **kw: True,
                    "default_return": False,
                },
            )
            with self.assertRaises(exceptions.OperatorImplementationOverrideError):
                DemoOp()

    def test_init_match_node(self):
        class DemoOp(Operator):
            name = "demo"
            default_return = False

            def implementation(self, *args):
                return True

            def init_match_node(cls, match_query, parse_func):
                pass

        with self.assertRaises(exceptions.OperatorImplementationInitMatchNodeError):
            DemoOp()


class TestOperator(TestCase):
    def setUp(self) -> None:
        self.dummy_args = (4, 2)

    def check_results(self, data, results, op):
        for d_p, res in zip(data, results):
            if isinstance(res, type) and issubclass(res, Exception):
                with self.assertRaises(res):
                    op(d_p)
            else:
                assert op(d_p) == res

    def test_expected_exc_single(self):
        exc = ValueError
        op = DemoOpModulo(*self.dummy_args, expected_exc=exc)
        assert op.expected_exc == {exc: op.default_return}

    def test_expected_exc_tuple(self):
        exc = ValueError, TypeError
        op = DemoOpModulo(*self.dummy_args, expected_exc=exc)
        assert op.expected_exc == {ex: op.default_return for ex in exc}

    def test_expected_exc_dict(self):
        exc = {ValueError: True, TypeError: False}
        op = DemoOpModulo(*self.dummy_args, expected_exc=exc)
        assert op.expected_exc == exc

    def test_expectec_exc_arg_error(self):
        exc = {ValueError: 23, TypeError: False}
        with self.assertRaises(exceptions.OperatorExpectedExcArgError):
            DemoOpModulo(*self.dummy_args, expected_exc=exc)
        with self.assertRaises(exceptions.OperatorExpectedExcArgError):
            DemoOpModulo(*self.dummy_args, expected_exc=[TypeError, EOFError])

    def test_expected_exc(self):
        data = [10, "1", 10.1, [], CursedData(PermissionError)]
        results = [True, TypeError, False, TypeError, False]
        op = DemoOpModulo(*self.dummy_args, expected_exc=PermissionError)
        self.check_results(data, results, op)

    def test_expected_exc_parent(self):
        class SubExc(PermissionError):
            pass

        data = [10, "1", 10.1, [], CursedData(SubExc)]
        results = [True, TypeError, False, TypeError, False]
        op = DemoOpModulo(*self.dummy_args, expected_exc=PermissionError)
        self.check_results(data, results, op)

    def test_expected_exc_mro(self):
        class BaseExcA(Exception):
            pass

        class BaseExcB(Exception):
            pass

        class SubExcA(BaseExcA, BaseExcB):
            pass

        class SubExcB(BaseExcB, BaseExcA):
            pass

        data = [CursedData(SubExcA), CursedData(SubExcB)]
        results = [False, True]
        op = DemoOpModulo(*self.dummy_args, expected_exc={BaseExcB: True, BaseExcA: False})
        for d_p, res in zip(data, results):
            assert op(d_p) == res

    def test_ignored_types_single(self):
        data = [10, "10", 10.0]
        op = DemoOpModulo(*self.dummy_args, ignored_types=int)
        self.check_results(data, [False, TypeError, True], op)

    def test_ignored_types_tuple(self):
        data = [10, "10", 10.0]
        op = DemoOpModulo(*self.dummy_args, ignored_types=(int, float))
        self.check_results(data, [False, TypeError, False], op)

    def test_ignored_types_error(self):
        for v in [1, (TypeError, 1)]:
            with self.assertRaises(exceptions.OperatorTypeCheckerError):
                DemoOpModulo(*self.dummy_args, ignored_types=v)

    def test_allowed_types_single(self):
        data = [10, "10", 10.0]
        op = DemoOpModulo(*self.dummy_args, allowed_types=int)
        self.check_results(data, [True, False, False], op)

    def test_allowed_types_tuple(self):
        data = [10, "10", 10.0]
        op = DemoOpModulo(*self.dummy_args, allowed_types=(int, float))
        self.check_results(data, [True, False, True], op)

    def test_allowed_types_error(self):
        for v in [1, (TypeError, 1)]:
            with self.assertRaises(exceptions.OperatorTypeCheckerError):
                DemoOpModulo(*self.dummy_args, allowed_types=v)


class TestCustomOp(TestCase):
    pass
