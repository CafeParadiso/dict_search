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
TAX_B = 0.2
TAX_C = 0.3
TAX_D = 0.4


PORT_ROTT = "Rotterdam"
PORT_LA = "Los Angeles"
PORT_VAL = "Valencia"
PORT_TANG = "Tanger"
PORT_BA = "Buenos Aires"
PORT_SH = "Shangai"

PAID_YES = ["Y", "Ye", "Yes", "YES", "yee"]
PAID_NO = ["N", "No", "NO", "n", "NN"]

data = [
    {
        "id": 1,
        "info": {
            "origin": COUNTRY_SPAIN,
            "ship_country": COUNTRY_SPAIN,
            "paid": PAID_YES[4],
            "arrival": datetime(2022, 6, 1),
        },
        "grouping": [
            {
                "company": COMPANY_MSK,
                "value": 10,
            },
            {
                "company": COMPANY_MSC,
                "value": 20,
            },
            {
                "company": COMPANY_HL,
                "value": 10,
            },
        ],
        "ports": (p for p in [PORT_VAL, PORT_ROTT, PORT_TANG]),
        "taxes": [TAX_C, TAX_D],
        "risky": CursedData(EOFError),
        "in_route": False,
    },
    {
        "id": 2,
        "info": {
            "origin": COUNTRY_INDONESIA,
            "ship_country": COUNTRY_SPAIN,
            "paid": PAID_YES[0],
            "arrival": datetime(2022, 7, 1),
        },
        "grouping": [
            {
                "company": COMPANY_MSK,
                "value": 10,
            },
            {
                "company": COMPANY_MSC,
                "value": 20,
            },
            {
                "company": COMPANY_HL,
                "value": 10,
            },
        ],
        "ports": [PORT_VAL, PORT_ROTT, PORT_TANG],
        "taxes": [TAX_B],
        "risky": CursedData(EOFError),
        "in_route": True,
    },
    {
        "id": 3,
        "info": {
            "origin": COUNTRY_SPAIN,
            "ship_country": COUNTRY_MORROCCO,
            "paid": PAID_YES[3],
            "arrival": datetime(2022, 8, 1),
        },
        "grouping": [
            {
                "company": COMPANY_MSK,
                "value": 10,
            },
            {
                "company": COMPANY_MSC,
                "value": 20,
            },
            {
                "company": COMPANY_HL,
                "value": 10,
            },
        ],
        "ports": (p for p in [PORT_VAL, PORT_ROTT, PORT_TANG]),
        "taxes": [TAX_C, TAX_A, TAX_B],
        "risky": 0,
        "in_route": True,
    },
]
