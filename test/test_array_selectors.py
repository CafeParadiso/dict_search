class TestArraySelectors:  # TODO test with data being a generator
    @staticmethod
    def test_index():
        values = DictSearch().dict_search(
            complex_data,
            {"posts": {"$index": {"0": {"interacted": {"$index": {"-1": {"type": "share"}}}}}}},
        )
        pprint(list(values))

    @staticmethod
    def test_range():
        for range_str, val, assert_val in [
            ("2:", 3, 2),
            ("2::", 3, 2),
            (":2", 2, 1),
            (":2:", 2, 1),
            ("::2", 1, 1),
            ("2:6", 3, 2),
            ("2:4:", 2, 2),
            ("2::2", 1, 3),
            (":4:2", 2, 2),
            ("2:5:2", 1, 3),
        ]:
            print(range_str)
            values = DictSearch().dict_search(
                range_data, {"mixed": {"a": {"$range": {range_str: {"$expr": lambda x: x.count(2) == val}}}}}
            )
            assert len(list(values)) == assert_val

    @staticmethod
    def test_where():
        values = DictSearch().dict_search(
           student_data, {"info": {"mentions": {"$where": [{"type": "angry"}, {"$all": {"score": 5}}]}}},
        )
        pprint(list(values))

    @staticmethod
    def test_where_eq():
        values = DictSearch().dict_search(
            student_data,
            {"c": "Territori", "tt": {"t": {"ff": {"f": {"$where": {"c": "Altitud"}}}}}},
        )
        pprint(list(values))

    #def test_where_eq_type_error
    #def test_where_not_found
    #def test_where_complex