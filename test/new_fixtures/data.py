from collections import namedtuple
from datetime import datetime
from . import CursedData

COUNTRY_INDONESIA = "Indonesia"
COUNTRY_SPAIN = "Spain"
COUNTRY_USA = "United States"
COUNTRY_ARGENTINA = "Argentina"
COUNTRY_MORROCCO = "Morrocco"

COMPANY_MSK = "Maersk"
COMPANY_HL = "Hapag-Loyd"
COMPANY_MSC = "MSC"
COMPANY_COSCO = "Cosco"
COMPANY_EVER = "Evergreen"

TAX_A = 0.1
TAX_B = 0.15
TAX_C = 0.20
TAX_D = 0.25


PORT_ROTT = "Rotterdam"
PORT_LA = "Los Angeles"
PORT_VAL = "Valencia"
PORT_TANG = "Tanger"
PORT_BA = "Buenos Aires"
PORT_SH = "Shangai"


PROD_CL = "Clothes"
PROD_CAR = "Cars"
PROD_GR = "Grains"
PROD_PC = "Computers"


def get_data():
    return [
        {
            "id": 1,
            "info": {
                "origin": COUNTRY_SPAIN,
                "ship_country": COUNTRY_SPAIN,
                "port_code": "SP-01-A1",
                "departure": datetime(2022, 6, 1),
            },
            "products": [
                {"product": PROD_GR, "due_date": datetime(2022, 7, 1), "cost": 10**6},
            ],
            "port_route": (p for p in [PORT_TANG, PORT_ROTT, PORT_TANG]),
            "in_route": False,
            "taxes": [TAX_B, TAX_C],
            "containers": [COMPANY_COSCO, COMPANY_MSC],
        },
        {
            "id": 2,
            "info": {
                "origin": COUNTRY_USA,
                "ship_country": COUNTRY_ARGENTINA,
                "port_code": "io-01-Ar21",
                "departure": datetime(2022, 3, 1),
            },
            "products": [
                {"product": PROD_PC, "due_date": datetime(2022, 4, 1), "cost": 10**5},
                {"product": PROD_PC, "due_date": datetime(2022, 6, 1), "cost": 20100},
                {"product": PROD_CAR, "due_date": datetime(2022, 6, 1), "cost": 56000},
            ],
            "port_route": [PORT_TANG, PORT_LA, PORT_TANG],
            "in_route": True,
            "taxes": [],
            "containers": [COMPANY_EVER, COMPANY_HL],
        },
        {
            "id": 3,
            "info": {
                "origin": COUNTRY_INDONESIA,
                "ship_country": COUNTRY_MORROCCO,
                "port_code": f"In_02_a1",
                "departure": datetime(2022, 5, 20),
            },
            "products": [
                {"product": PROD_PC, "due_date": datetime(2022, 7, 1)},
                {"product": PROD_GR, "due_date": datetime(2022, 4, 1), "cost": 234000},
            ],
            "port_route": (p for p in [PORT_VAL, PORT_ROTT, PORT_TANG]),
            "in_route": False,
            "taxes": (TAX_C, TAX_D, TAX_B),
            "containers": [COMPANY_COSCO, COMPANY_HL, COMPANY_MSK],
        },
        {
            "id": 4,
            "info": {
                "origin": COUNTRY_USA,
                "ship_country": COUNTRY_MORROCCO,
                "port_code": "sp-02-b1",
                "departure": datetime(2022, 6, 1),
            },
            "products": [
                {"product": PROD_GR, "due_date": datetime(2022, 7, 1), "cost": 55000},
                {"product": PROD_PC, "due_date": datetime(2022, 7, 1), "cost": 34000},
                {"product": PROD_PC, "due_date": datetime(2022, 7, 1), "cost": 40000},
                {"product": PROD_GR, "due_date": datetime(2022, 7, 20), "cost": 35000},
                {"product": PROD_CAR, "due_date": datetime(2022, 6, 5), "cost": 50000},
            ],
            "port_route": (p for p in [PORT_LA, PORT_SH, PORT_ROTT, PORT_LA]),
            "in_route": True,
            "taxes": [TAX_A],
            "containers": [COMPANY_HL],
        },
        {
            "id": 5,
            "info": {
                "origin": COUNTRY_USA,
                "ship_country": COUNTRY_SPAIN,
                "port_code": "sp-02-A1",
                "departure": datetime(2022, 6, 20),
            },
            "products": [
                {"product": PROD_CAR, "cost": 10**5},
                {"product": PROD_CAR, "cost": 250000},
                {"product": PROD_CAR,  "cost": 500000},
            ],
            "port_route": (p for p in [PORT_SH, PORT_BA, PORT_ROTT]),
            "in_route": True,
            "taxes": [TAX_D, TAX_C],
            "containers": [COMPANY_MSC, COMPANY_MSK],
        },
        {
            "id": 6,
            "info": {
                "origin": COUNTRY_SPAIN,
                "ship_country": COUNTRY_MORROCCO,
                "port_code": "MR-02-A2",
                "departure": datetime(2022, 6, 1),
            },
            "products": [
                {"product": PROD_GR, "due_date": datetime(2022, 7, 1), "cost": 10**6},
            ],
            "port_route": (p for p in [PORT_VAL, PORT_ROTT, PORT_TANG]),
            "in_route": False,
            "taxes": [TAX_B, TAX_C],
            "containers": [],
        },
        {
            "id": 7,
            "info": {
                "origin": COUNTRY_SPAIN,
                "port_code": "MR-02-A2",
                "departure": datetime(2022, 6, 1),
            },
            "products": [],
            "port_route": (p for p in [PORT_VAL, PORT_ROTT, PORT_TANG]),
            "in_route": False,
            "taxes": [TAX_B, TAX_C],
            "containers": [],
        },
    ]
