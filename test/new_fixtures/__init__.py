import json
import random
import re
import datetime
from os import listdir, path
import uuid


def build_fixtures(n_docs):
    countries = ["Spain", "Italy", "Sudan", "USA", "Zimbawe", "Indonesia", "Peru", "Haiti", "Russia", "Albania"]
    products_list = ["BMW", "Mercedes", "Audi", "Porsche", "Mustang", "Kawasaki", "Bentley", "Maybach", "Aston Martin"]
    status = ["Partial", "ToProcess", "Finished", "Expired"]
    incoterms = ["EXW" "FCA", "CPT", "CIP", "DAP", "DPU", "DDP"]
    taxes = [
        {"type": "VAT", "value": random.randint(5, 20)},
        {"type": "Exp_tariff", "value": 10},
        {"type": "Imp_tariff", "value": 10},
        {"type": "Special Tax", "value": random.randint(1, 25)},
        {"type": "Bribe", "value": random.randint(1, 25)},
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

    for _ in range(n_docs):
        random.shuffle(taxes)
        random.shuffle(ports_list)
        random.shuffle(products_list)
        # info
        info = {
            "origin": random.choice(countries),
            random.choice(
                ["Inco", "incoterms", "terms", "INCO", "ITerms", "iterms", "icoterms", "Terms"]
            ): random.choice(incoterms),
            "paid": random.choice(["Y", "y", "yes", "YES", "N", "n", "no", "NO", "yee", "yss", "nn"]),
            "arrival": random_date(),
        }

        # create port list generator
        used_ports = [{"port": port, "days": random.randint(5, 45)} for port in ports_list[0 : random.randint(0, 7)]]
        if random.randint(0, 1):
            used_ports = []
        else:
            used_ports.append(random.choice(ports_list))

        # create cargo
        products = []
        for __ in range(random.randint(1, 6)):
            product = {
                "uuid": uuid.uuid4(),
                "product": random.choice(products_list),
                "weight": random.randint(500, 1500),
                "suspicious": random.choice(["yes", "no", CursedData()]),
                "origin": random.choice(countries),
            }
            if random.randint(0, 1):
                product["due_delivery"] = random_date()
            if random.randint(0, 1):
                product["status"] = random.choice(status)
            if random.randint(0, 1):
                product["variations"] = [
                    {
                        "type": random.choice(["A", "B", "C", "D"]),
                        "units": random.randint(1, 100),
                    }
                    for _ in range(random.randint(1, 5))
                ]
            if random.randint(0, 1):
                product["size"] = f"{random.randint(5, 15)}X{random.randint(5, 15)}X{random.randint(5, 15)}"
            if random.randint(0, 1):
                product["transport_cost"] = random.randint(1000, 2000)
            products.append(product)
        cargo = {
            "products": products,
        }
        document = {
            "id": _,
            "info": info,
            "cargo": cargo,
            "ports": used_ports,
            "combustible_usage(L)": random.randint(5000, 15000),
            "checksum": [
                random.choice(["1", "2", "3", 1, 2, 3, 1.1, 2.2, 3.3, complex(1), complex(2), complex(3)])
                for _ in range(random.randint(2, 6))
            ],
            "reviewed": random.choice([0, 1, True, False, "y", "n", CursedData()]),
        }
        if random.randint(0, 1):
            document["taxes"] = [d for d in taxes[: random.randint(1, len(taxes) - 1)]]
        if random.randint(0, 1):
            document["banned_countries"] = [random.choice(countries) for _ in range(random.randint(1, 3))]
        document.update(
            random.choice(
                [
                    {"crew": random.randint(5, 20)},
                    {"passengers": {"cabin": {"crew": random.randint(5, 20)}, "leisure": 0}},
                    {"personnel": {"crew": random.randint(5, 20), "cleanup": random.randint(1, 5)}},
                ]
            )
        )
        print(document)
        with open(f"{_}.json", "w") as file:
            json.dump(document, file, indent=4, default=str)


class CursedData:
    """Class to emulate bad behavioured objects found in the wild"""

    def __init__(self, exc=Exception):
        self._exc = exc

    def __bool__(self):
        raise self._exc

    def __eq__(self, other):
        raise self._exc

    def __gt__(self, other):
        raise self._exc

    def __lt__(self, other):
        raise self._exc

    def __index__(self):
        raise self._exc

    def __mod__(self, other):
        raise self._exc

    def __contains__(self, item):
        raise self._exc

    def __instancecheck__(self, instance):
        raise self._exc


def random_date():
    return datetime.datetime(2022, random.randint(6, 11), random.randint(1, 30))


def ports(ports_list):
    for port in ports_list:
        yield port


def custom_decoder(dikt):
    pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})")
    for k in dikt:
        if isinstance(dikt[k], str) and "__main__.CursedData" in dikt[k]:
            dikt[k] = CursedData(BrokenPipeError)
        elif isinstance(dikt[k], str) and pattern.match(dikt[k]):
            groups = pattern.match(dikt[k]).groups()
            dikt[k] = datetime.datetime(int(groups[0]), int(groups[1]), int(groups[2]))
        elif k == "ports":
            dikt[k] = ports(dikt[k])
    return dikt


def read_fixtures():
    directory = path.join(path.dirname(__file__), "")
    for file in list(filter(lambda x: ".json" in x, listdir(directory))):
        with open(path.join(directory, file), "r") as fp:
            yield json.load(fp, object_hook=custom_decoder)
