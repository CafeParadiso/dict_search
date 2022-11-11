def func(x, y):
    return x == y


class EqCall:
    def __init__(self):
        pass

    def __call__(self, x, y):
        return x == y


class EqMeth:
    def __init__(self):
        pass

    def sum(self, x, y):
        return x == y


class EqMp:
    def __init__(self):
        self.__class__.__call__ = self.sum

    def __call__(self, x, y):
        return x == y

    def sum(self, x, y):
        return x == y


if __name__ == '__main__':
    import timeit
    eq = EqCall()
    eq_m = EqMeth()
    eq_mp = EqMp()
    n = 5000000
    data = [1, 2, "1", 2, []]
    print(f"Lambda {timeit.timeit(lambda: list(map(lambda x: x == 2 ,data)), number=n)}")
    print(f"Eq {timeit.timeit(lambda: list(map(lambda x: eq(x, 2), data)), number=n)}")
    print(f"Eq m {timeit.timeit(lambda: list(map(lambda x: eq_m.sum(x, 2), data)), number=n)}")
    print(f"Eq mp {timeit.timeit(lambda: list(map(lambda x: eq_mp(x, 2), data)), number=n)}")
    print(f"Func {timeit.timeit(lambda: list(map(lambda x: func(x, 2), data)), number=n)}")