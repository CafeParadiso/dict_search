import re

RANGE_PATTERNS = [
    re.compile(rf"^(-?\d+)::?$"),
    re.compile(rf"^:(-?\d+):?$"),
    re.compile(rf"^::(-?\d+)$"),
    re.compile(rf"^(-?\d+):(-?\d+):?$"),
    re.compile(rf"^(-?\d+)::(-?\d+)$"),
    re.compile(rf"^:(-?\d+):(-?\d+)$"),
    re.compile(rf"^(-?\d+):(-?\d+):(-?\d+)$"),
    re.compile(r"^:$"),
]
