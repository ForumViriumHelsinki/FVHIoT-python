# https://github.com/decentlab/decentlab-decoders/blob/master/DL-TBRG/DL-TBRG%20(resolution%3D0.1).py
import binascii
import datetime
import struct
from typing import Optional
from zoneinfo import ZoneInfo

# device-specific parameters
PARAMETERS = {"resolution": 0.1}

PROTOCOL_VERSION = 2

# Do not change the names below
SENSORS = [
    {
        "length": 4,
        "values": [
            {"name": "precipitation", "convert": lambda x: x[0] * PARAMETERS["resolution"]},
            {"name": "precipitation_interval", "convert": lambda x: x[1]},
            {
                "name": "precipitation_cumulative",
                "convert": lambda x: (x[2] + x[3] * 65536) * PARAMETERS["resolution"],
            },
        ],
    },
    {"length": 1, "values": [{"name": "battery", "convert": lambda x: x[0] / 1000}]},
]

# TODO: the function body is clone of the one in dlmbx.py and others. Refactor to avoid duplication.
def parse_dlmbx(hex_str: str, port: int):
    """hex_str: payload as hex string"""
    bytes_ = bytearray(binascii.a2b_hex(hex_str))
    version = bytes_[0]
    if version != PROTOCOL_VERSION:
        raise ValueError("protocol version {} doesn't match v2".format(version))

    devid = struct.unpack(">H", bytes_[1:3])[0]
    bin_flags = bin(struct.unpack(">H", bytes_[3:5])[0])
    flags = bin_flags[2:].zfill(struct.calcsize(">H") * 8)[::-1]
    words = [struct.unpack(">H", bytes_[i : i + 2])[0] for i in range(5, len(bytes_), 2)]

    cur = 0
    result = {"dl_id": devid, "protocol": version}  # Decent lab device id
    for flag, sensor in zip(flags, SENSORS):
        if flag != "1":
            continue

        x = words[cur : cur + sensor["length"]]
        cur += sensor["length"]
        for value in sensor["values"]:
            if "convert" not in value:
                continue
            result[value["name"]] = value["convert"](x)

    return result


def decode_hex(hex_str: str, port: int):
    return parse_dlmbx(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "dl_id": 6359,
          "protocol": 2,
          "distance": 2517,
          "valid_samples": 15,
          "batt": 2.756
        }
      }
    ]
    """
    values = decode_hex(hex_str, port)
    dataline = {"time": time_str, "data": values}
    datalines = [dataline]
    return datalines


def main(samples: list):
    now = datetime.datetime(2022, 3, 2, 12, 21, 30, 123000, tzinfo=ZoneInfo("UTC")).isoformat()
    if len(sys.argv) == 3:
        print(json.dumps(create_datalines(sys.argv[1], int(sys.argv[2]), now), indent=2))
    else:
        print("Some examples:")
        for s in samples:
            try:
                print("{}:{} --> {}".format(s[0], s[1], json.dumps(create_datalines(s[0], s[1], now), indent=2)))
            except ValueError as err:
                print(f"Invalid payload + FPort '{s[0]}:{s[1]}' or payload size {len(s[0])}: {err}")
        print(f"\nUsage: {sys.argv[0]} hex_payload port\n\n")


if __name__ == "__main__":
    import json
    import sys

    examples = [
        ["0202f8000300040258409a00000c54", 1],
        ["0202f800020c54", 1],
        ["025582000300000258000000000c3e", 1],
    ]
    main(examples)
