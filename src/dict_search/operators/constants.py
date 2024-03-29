import re

SLICING_PATTERN = re.compile(
    r"^(-?\d+)::?$|"
    r"^:(-?\d+):?$|"
    r"^::(-?\d+)$|"
    r"^(-?\d+):(-?\d+):?$|"
    r"^(-?\d+)::(-?\d+)$|"
    r"^:(-?\d+):(-?\d+)$|"
    r"^(-?\d+):(-?\d+):(-?\d+)$|"
    r"^:$"
)

CONTAINER_TYPE = list
