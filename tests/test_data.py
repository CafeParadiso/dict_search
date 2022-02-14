from pprint import pprint
import random


data = [
    {
        "assets": {"curr": {"a": 0, "b": 0}, "non_cur": 4355},
        "fy": 2011,
        "liab": {"cur": 3265, "non_cur": {"a": 18498}},
        "name": "gld",
        "special": [0.2931003361010066, 0.8628788818575526, 0.25272849318902857, 0.7586199014105721],
    },
    {
        "assets": {"curr": {"a": 0, "b": 0}, "non_cur": 4586},
        "fy": 2013,
        "liab": {"cur": 2952, "non_cur": {"a": 2447}},
        "name": "mdb",
        "special": False,
    },
    {
        "assets": {"curr": {"a": 0, "b": 0}, "non_cur": 2545},
        "fy": 2014,
        "liab": {"cur": 2830, "non_cur": {"a": 14914}},
        "name": "estc",
        "special": False,
    },
    {
        "assets": {"curr": {"a": 1, "b": 0}, "non_cur": 1584},
        "fy": 2014,
        "liab": {"cur": 4978, "non_cur": {"a": 17080}},
        "name": "akam",
        "special": False,
    },
    {
        "assets": {"curr": {"a": 0, "b": 1}, "non_cur": 3881},
        "fy": 2011,
        "liab": {"cur": 3661, "non_cur": {"a": 9472}},
        "name": "msft",
        "special": False,
    },
    {
        "assets": {"curr": {"a": 0, "b": 0}, "non_cur": 3705},
        "fy": 2012,
        "liab": {"cur": 4259, "non_cur": {"a": 5514}},
        "name": "appl",
        "special": False,
    },
    {
        "assets": {"curr": {"a": 1, "b": 0}, "non_cur": 3984},
        "fy": 2013,
        "liab": {"cur": 4034, "non_cur": {"a": 11843}},
        "name": "tsm",
        "special": True,
    },
    {
        "assets": {"curr": {"a": 1, "b": 0}, "non_cur": 3922},
        "fy": 2011,
        "liab": {"cur": 2085, "non_cur": {"a": 11901}},
        "name": "asml",
        "special": [
            0.9541537831503751,
            0.23165716836983463,
            0.296616400864381,
            0.3856594791597231,
            0.41055831159083733,
        ],
    },
]


def build_test_data():
    name = ["mdb", "akam", "goog", "appl", "msft", "gld", "ibm", "tsm", "asml", "estc", "gm"]
    for _ in range(8):
        d = {
            "name": random.choice(name),
            "assets": {
                "curr": {
                    "a": random.randrange(0, 2),
                    "b": random.randrange(0, 2),
                },
                "non_cur": random.randrange(1000, 5000),
            },
            "liab": {
                "cur": random.randrange(1000, 5000),
                "non_cur": {
                    "a": random.randrange(2000, 20000),
                },
            },
            "fy": random.randrange(2010, 2015),
            "special": [random.random() for _ in range(random.randrange(2, 6))]
            if random.random() > 0.5
            else random.choice([True, False]),
        }
        pprint(d)


if __name__ == "__main__":
    build_test_data()
