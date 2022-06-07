import datetime
import json
from os import path
from os import listdir
import random
import re
import uuid

from pprint import pprint

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
    {"mixed": {"a": 1}},
]

student_data = [
    {
        "id": 0,
        "info": {
            "full_name": {"first": "Jones", "last": "BigL"},
            "h": 180,
            "mentions": [{"score": 1, "type": "angry"}, {"score": 5, "type": "angry"}],
            "w": 70,
        },
        "status": "graduating",
        "subjects": ["Sports", "Spanish", "English", "Maths"],
    },
    {
        "id": 1,
        "info": {
            "full_name": {"first": "Snoop", "last": "Soulja"},
            "h": 204,
            "mentions": [
                {"score": 5, "type": "angry"},
                {"score": 5, "type": "angry"},
                {"score": 2, "type": "active"},
                {"score": 2, "type": "active"},
            ],
            "w": 84,
        },
        "status": "expelled",
        "subjects": ["English", "Chemistry", "Spanish", "Music"],
    },
    {
        "id": 2,
        "info": {
            "full_name": {"first": "Dogg", "last": "Snoop"},
            "h": 166,
            "mentions": [
                {"score": 5, "type": "active"},
                {"score": 8, "type": "eloquent"},
                {"score": 9, "type": "passive"},
                {"score": 3, "type": "angry"},
            ],
            "w": 68,
        },
        "status": "graduated",
        "subjects": ["Spanish", "Chemistry"],
    },
    {
        "id": 3,
        "info": {
            "full_name": {"first": "Southside", "last": "Snoop"},
            "h": 179,
            "mentions": [{"score": 10, "type": "eloquent"}],
            "w": 71,
        },
        "status": "graduating",
        "subjects": ["English", "Music", "Spanish", "Sports"],
    },
]


class CursedData:
    """Class to emulate bad behavioured objects found in the wild"""

    def __bool__(self):
        raise ValueError("The truth value is ambiguous")


def build_fixtures(vals):
    names = ["Snoop", "BigL", "Gucc", "Lex", "Southside", "Fat", "Mike", "Joe", "Dogg", "Jones", "Montana", "Soulja"]
    countries = ["Spain", "Italy", "Sudan", "USA", "Zimbawe", "Indonesia", "Peru", "Haiti", "Russia", "Albania"]
    sizes = [100, 150, 200, 250]
    products = ["Furnitures", "Cars", "Iron", "Guns", "Sugar", "Wooden", "Grain", "Coffe", "Oil", "Chips", "Cement"]
    status = ["Partial", "ToProcess", "Finished", "Expired"]
    incoterms = ["EXW" "FCA", "CPT", "CIP", "DAP", "DPU", "DDP"]
    taxes = [
        {"type": "VAT", "value": random.randint(5, 20)},
        {"type": "Exp_tariff", "value": 10},
        {"type": "Imp_tariff", "value": 10},
        {"type": "Special Tax", "value": random.randint(1, 25)},
        {"type": "Bribe", "value": random.randint(0, 25)},
    ]
    ports_list = [
        "Shangai",
        "Shenzen",
        "Busan",
        "Rotterdam",
        "Jebel Ali",
        "Los Angeles",
        "Valencia",
        "Manila",
        "Algeciras",
        "Cape Town",
    ]
    for _ in range(vals):
        random.shuffle(taxes)
        random.shuffle(ports_list)
        used_ports = ports_list[0:random.randint(0, 5)]
        document = {
            "id": _,
            "shipping_date": datetime.datetime(2022, random.randint(1, 12), random.randint(1, 28)),
            "customer_name": {"first": random.choice(names), "last": random.choice(names)},
            "info": {
                "origin": random.choice(countries),
                "desination": random.choice(countries),
                "suspicious": random.choice([True, False, CursedData()]),
                "container": random.choice(
                    [
                        f"{random.choice(sizes)}x{random.choice(sizes)}",
                        [random.choice(sizes), random.choice(sizes)],
                        {"w": random.choice(sizes), "h": random.choice(sizes)},
                    ]
                ),
            },
            "batch": {
                "products": [
                    random.choice(
                        [
                            {
                                "product": random.choice(products),
                                "types": [
                                    {
                                        "type": random.choice(["A", "B", "C"]),
                                        "qtty": random.randint(1, 20),
                                        "price": random.randint(500, 2000),
                                    }
                                    for _ in range(random.randint(0, 5))
                                ],
                                "status": random.choice(status),
                            },
                            {
                                "product": random.choice(products),
                                "types": [
                                    {
                                        "type": random.choice(["A", "B", "C"]),
                                        "qtty": random.randint(1, 20),
                                        "price": random.randint(1, 1000),
                                    }
                                    for _ in range(random.randint(0, 5))
                                ],
                                "due": datetime.datetime(2022, random.randint(1, 12), random.randint(1, 28)),
                            },
                            {
                                "product": random.choice(products),
                                "uuid": uuid.uuid4(),
                            },
                        ]
                    )
                    for _ in range(random.randint(1, 9))
                ],
                "wholesale_value": random.randint(10000, 100000),
            },
            "taxes": taxes[: random.randint(1, 5)],
            random.choice(
                ["Inco", "incoterms", "terms", "INCO", "ITerms", "iterms", "icoterms", "Terms"]
            ): random.choice(incoterms),
            "paid": random.choice(["Y", "y", "yes", "YES", "N", "n", "no", "NO"]),
            "port_route": (ports(used_ports), used_ports),
        }
        document.update(
            random.choice(
                [
                    {"producer_country": random.choice(countries)},
                    {"arrival_date": document["shipping_date"] + datetime.timedelta(days=random.randint(30, 120))},
                ]
            )
        )
        with open(path.join("fixtures", f"{_}.json"), "w") as file:
            json.dump(document, file, indent=4, default=str)


def ports(ports_list):
    random.shuffle(ports_list)
    for port in ports_list[0:random.randint(0, 5)]:
        yield port


def custom_decoder(dikt):
    pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})")
    for k in dikt:
        if isinstance(dikt[k], str) and "__main__.CursedData" in dikt[k]:
            dikt[k] = CursedData()
        elif isinstance(dikt[k], str) and pattern.match(dikt[k]):
            groups = pattern.match(dikt[k]).groups()
            dikt[k] = datetime.datetime(int(groups[0]), int(groups[1]), int(groups[2]))
        elif k == "port_route":
            dikt[k] = ports(dikt[k][1])
    return dikt


def read_fixtures():
    directory = path.join(path.dirname(__file__), "fixtures")
    for file in listdir(directory):
        with open(path.join(directory, file), "r") as fp:
            yield json.load(fp, object_hook=custom_decoder)


if __name__ == "__main__":
    build_fixtures(10)
