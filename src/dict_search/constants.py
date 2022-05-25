import re

S, E, ST = "start", "end", "step"
RE_RANGE_S = re.compile(rf"^(?P<{S}>-?\d+)::?$")
RE_RANGE_E = re.compile(rf"^:(?P<{E}>-?\d+):?$")
RE_RANGE_ST = re.compile(rf"^::(?P<{ST}>-?\d+)$")
RE_RANGE_SE = re.compile(rf"^(?P<{S}>-?\d+):(?P<{E}>-?\d+):?$")
RE_RANGE_SST = re.compile(rf"^(?P<{S}>-?\d+)::(?P<{ST}>-?\d+)$")
RE_RANGE_EST = re.compile(rf"^:(?P<{E}>-?\d+):(?P<{ST}>-?\d+)$")
RE_RANGE_SEST = re.compile(rf"^(?P<{S}>-?\d+):(?P<{E}>-?\d+):(?P<{ST}>-?\d+)$")
RE_RANGE_ALL = re.compile(r"^:$")
