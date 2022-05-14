import json

from pprint import pprint
import random

import datetime

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

complex_data = [
    {
        "id": 0,
        "posts": [
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 5, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 1, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 1, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 20, 0, 0), "type": "share"},
                ],
                "post_id": 0,
                "text": "tsm",
            },
            {
                "interacted": [{"date": datetime.datetime(2022, 1, 19, 0, 0), "type": "post"}],
                "post_id": 1,
                "text": "gld",
            },
        ],
        "user": {"id": 141},
        "values": [-0.4554757888427883, 0.624596827960479],
    },
    {
        "id": 1,
        "posts": [
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 31, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 1, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 28, 0, 0), "type": "post"},
                ],
                "post_id": 0,
                "text": "aaoi",
            }
        ],
        "user": {"id": 141},
        "values": [
            0.27584865512836887,
            1.4732722258715452,
            1.2109810927030629,
            0.7939559412247775,
            -0.5491601506745909,
        ],
    },
    {
        "id": 2,
        "posts": [
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 28, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 12, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 13, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 21, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 23, 0, 0), "type": "post"},
                ],
                "post_id": 0,
                "text": "gld",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 18, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 5, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 18, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 8, 0, 0), "type": "share"},
                ],
                "post_id": 1,
                "text": "akam",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 8, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 17, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 9, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 28, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 19, 0, 0), "type": "keep"},
                ],
                "post_id": 2,
                "text": "gm",
            },
        ],
        "user": {"id": 94},
        "values": [1.557726481970398, 0.948670504350301, 1.4782528602442442],
    },
    {
        "id": 3,
        "posts": [
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 8, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 14, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 31, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 14, 0, 0), "type": "keep"},
                ],
                "post_id": 0,
                "text": "gm",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 23, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 17, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 17, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 3, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 2, 0, 0), "type": "keep"},
                ],
                "post_id": 1,
                "text": "msft",
            },
        ],
        "user": {"id": 68},
        "values": [1.4315910403254501, 0.9723804444991478, 0.61546180581964538],
    },
    {
        "id": 4,
        "posts": [
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 2, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 10, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 22, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 23, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 18, 0, 0), "type": "keep"},
                ],
                "post_id": 0,
                "text": "gld",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 5, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 15, 0, 0), "type": "keep"},
                ],
                "post_id": 1,
                "text": "appl",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 29, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 27, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 13, 0, 0), "type": "post"},
                ],
                "post_id": 2,
                "text": "aaoi",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 2, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 20, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 2, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 9, 0, 0), "type": "share"},
                ],
                "post_id": 3,
                "text": "asml",
            },
        ],
        "user": {"id": 176},
        "values": [
            -0.5432711348081195,
            1.2479296758010348,
            0.18648724503783387,
            1.104727543041008,
            -0.13609632624809476,
        ],
    },
    {
        "id": 5,
        "posts": [
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 13, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 5, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 28, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 10, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 7, 0, 0), "type": "share"},
                ],
                "post_id": 0,
                "text": "akam",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 14, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 18, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 16, 0, 0), "type": "keep"},
                ],
                "post_id": 1,
                "text": "mdb",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 2, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 10, 0, 0), "type": "post"},
                ],
                "post_id": 2,
                "text": "mdb",
            },
        ],
        "user": {"id": 143},
        "values": [-0.509986019526338, 0.48027375218726875, 1.7508556683888716, 0.5473434127045574, 1.7692071208685431],
    },
    {
        "id": 6,
        "posts": [
            {
                "interacted": [{"date": datetime.datetime(2022, 1, 18, 0, 0), "type": "post"}],
                "post_id": 0,
                "text": "mdb",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 15, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 19, 0, 0), "type": "post"},
                ],
                "post_id": 1,
                "text": "appl",
            },
            {
                "interacted": [{"date": datetime.datetime(2022, 1, 24, 0, 0), "type": "share"}],
                "post_id": 2,
                "text": "mdb",
            },
        ],
        "user": {"id": 478},
        "values": [0.17672849905498556, 1.158563924131046],
    },
    {
        "id": 7,
        "posts": [
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 3, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 22, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 25, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 12, 0, 0), "type": "post"},
                    {"date": datetime.datetime(2022, 1, 11, 0, 0), "type": "share"},
                ],
                "post_id": 0,
                "text": "mdb",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 24, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 11, 0, 0), "type": "keep"},
                    {"date": datetime.datetime(2022, 1, 8, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 9, 0, 0), "type": "post"},
                ],
                "post_id": 1,
                "text": "asml",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 7, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 12, 0, 0), "type": "share"},
                ],
                "post_id": 2,
                "text": "aaoi",
            },
            {
                "interacted": [
                    {"date": datetime.datetime(2022, 1, 22, 0, 0), "type": "share"},
                    {"date": datetime.datetime(2022, 1, 8, 0, 0), "type": "post"},
                ],
                "post_id": 3,
                "text": "msft",
            },
        ],
        "user": {"id": 7},
        "values": [-0.9795149399926325, 0.4925599211086731, -0.6872335333848887],
    },
]

range_data = [
    {
        "mixed": {
            "a": [0, 1, 2, 0, 1, 2],
        }
    },
    {
        "mixed": {
            "a": [2, 2, 2, 2, 1, 2],
        }
    },
    {
        "mixed": {
            "a": [2, 0, 2, 2, 1, 2],
        }
    },
    {
        "mixed": {
            "a": 1
        }
    },
]


def gene_data():
    data = None
    with open(r"C:\Users\mike_\Desktop\house_search\raw_data\080018.json", encoding="utf-8") as file:
        data = json.load(file)
    return data


def build_simple_data():  # pragma: no cover
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


def build_complex_data():    # pragma: no cover
    name = ["mdb", "akam", "goog", "appl", "msft", "gld", "ibm", "tsm", "asml", "estc", "gm", "aaoi", "akam"]
    values = []
    for _ in range(8):
        d = {
            "id": _,
            "posts": [
                {
                    "post_id": idx,
                    "text": random.choice(name),
                    "interacted": [
                        {
                            "type": random.choice(["share", "post", "keep"]),
                            "date": datetime.datetime(2022, 1, random.randint(1, 31)),
                        }
                        for i in range(random.randint(1, 5))
                    ],
                }
                for idx in range(random.randint(1, 5))
            ],
            "user": {"id": hash(random.choice(name)) % random.randint(1, 1000)},
            "values": [random.random() + random.randint(-1, 1) for x in range(random.randint(2, 5))],
        }

        values.append(d)
    pprint(values)


if __name__ == "__main__":
    def t(x):
        for _ in range(x):
            yield None
    print(all(0))
