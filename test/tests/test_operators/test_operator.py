from src.dict_search import Operator
from test.utils import TestCase, TestOpModulo
from test.new_fixtures import CursedData
from src.dict_search.operators import exceptions


class TestOperatorImplementation(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestOperatorImplementation, self).__init__(*args, **kwargs)
        self.implementation_key = Operator.implementation.__name__
        self.initial_def_key = Operator.initial_default_return.fget.__name__
        self.name_key = Operator.name.fget.__name__

    def test_correct_instantiation(self):
        assert TestOpModulo()

    def test_abstract_class_error(self):
        op = type(f"TestOp", (Operator, *Operator.__bases__), {})
        with self.assertRaises(TypeError):
            op()

    def test_name_error(self):
        op = type(
            f"TestOp",
            (Operator, *Operator.__bases__),
            {self.initial_def_key: True, self.name_key: 1, self.implementation_key: lambda: ...},
        )
        with self.assertRaises(exceptions.OperatorImplementationNameError):
            op()

    def test_classattr_type_error(self):
        for attrs_dict in [
            {self.initial_def_key: lambda: ..., self.name_key: "testop"},
            {self.initial_def_key: property(), self.name_key: "testop"},
            {self.initial_def_key: False, self.name_key: property()},
            {self.initial_def_key: True, self.name_key: lambda: ...},
        ]:
            op = type(
                f"TestOp",
                (Operator, *Operator.__bases__),
                {**attrs_dict, self.implementation_key: lambda *args, **kw: False},
            )
            with self.assertRaises(exceptions.OperatorImplementationAttrTypeError):
                op()

    def test_override_error(self):
        op = type(
            f"TestOp",
            (Operator, *Operator.__bases__),
            {
                self.initial_def_key: True,
                self.name_key: "test",
                self.implementation_key: lambda: ...,
                Operator.allowed_types.fget.__name__: "2",
            },
        )
        with self.assertRaises(exceptions.OperatorImplementationOverrideError):
            op()

    def test_override(self):
        op = type(
            f"TestOp",
            (Operator, *Operator.__bases__),
            {
                self.initial_def_key: True,
                self.name_key: "test",
                self.implementation_key: lambda: ...,
                Operator.precondition.__name__: lambda: ...,
                "extra": lambda: ...,
            },
        )
        op()


class TestOperator(TestCase):
    def test_expected_exc_single(self):
        exc = ValueError
        op = TestOpModulo(expected_exc=exc)
        assert op.expected_exc == {exc: op.default_return}

    def test_expected_exc_tuple(self):
        exc = ValueError, TypeError
        op = TestOpModulo(expected_exc=exc)
        assert op.expected_exc == {ex: op.default_return for ex in exc}

    def test_expected_exc_dict(self):
        exc = {ValueError: True, TypeError: False}
        op = TestOpModulo(expected_exc=exc)
        assert op.expected_exc == exc

    def test_expectec_exc_arg_error(self):
        exc = {ValueError: 23, TypeError: False}
        with self.assertRaises(exceptions.OperatorExpectedExcArgError):
            TestOpModulo(expected_exc=exc)
        with self.assertRaises(exceptions.OperatorExpectedExcArgError):
            TestOpModulo(expected_exc=[TypeError, EOFError])

    def test_expected_exc(self):
        data = [10, "1", 10.1, [], CursedData(PermissionError)]
        results = [True, TypeError, False, TypeError, False]
        q = (4, 2)
        op = TestOpModulo(expected_exc=PermissionError)
        for d_p, res in zip(data, results):
            if isinstance(d_p, (list, str)):
                with self.assertRaises(res):
                    op(d_p, *q)
            else:
                assert op(d_p, *q) == res

    def test_expected_exc_subclass(self):
        data = [10, "1", 10.1, [], CursedData(PermissionError)]
        results = [True, False, False, False, False]
        q = (4, 2)
        op = TestOpModulo(expected_exc=Exception)
        for d_p, res in zip(data, results):
            assert op(d_p, *q) == res

    def test_expected_exc_subclass_order(self):
        class DemoExc(TypeError):
            pass

        data = [10, "1", CursedData(DemoExc)]
        results = [True, True, False]
        q = (4, 2)
        op = TestOpModulo(expected_exc={Exception: False, TypeError: True})
        for d_p, res in zip(data, results):
            assert op(d_p, *q) == res
        results = [True, True, True]
        op = TestOpModulo(expected_exc={TypeError: True, Exception: False})
        for d_p, res in zip(data, results):
            assert op(d_p, *q) == res

    def test_default_return_type_error(self):
        with self.assertRaises(exceptions.OperatorDefaultReturnError):
            TestOpModulo(default_return={})

    def test_ignored_types(self):
        data = [10, "1", 10.0]
        q = 4, 2
        op = TestOpModulo(ignored_types=int)
        for d_p, v in zip(data, [False, False, True]):
            if isinstance(d_p, str):
                continue
            assert op(d_p, *q) == v
        op.ignored_types = None
        for d_p, v in zip(data, [True, False, True]):
            if isinstance(d_p, str):
                continue
            assert op(d_p, *q) == v
        op.ignored_types = int
        for d_p, v in zip(data, [False, False, True]):
            if isinstance(d_p, str):
                continue
            assert op(d_p, *q) == v

    def test_ignored_types_error(self):
        with self.assertRaises(exceptions.OperatoTypeCheckerError):
            TestOpModulo(ignored_types=[int, str])

    def test_allowed_types(self):
        data = [10, "1", 10.0]
        q = 4, 2
        op = TestOpModulo(allowed_types=int)
        for d_p, v in zip(data, [True, False, False]):
            assert op(d_p, *q) == v
        op.allowed_types = None
        for d_p, v in zip(data, [True, False, True]):
            if isinstance(d_p, str):
                continue
            assert op(d_p, *q) == v
        op.allowed_types = int
        for d_p, v in zip(data, [True, False, False]):
            assert op(d_p, *q) == v

    def test_allowed_types_error(self):
        with self.assertRaises(exceptions.OperatoTypeCheckerError):
            TestOpModulo(allowed_types=[int, str])
