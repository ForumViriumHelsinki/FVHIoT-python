"""
https://github.com/decentlab/decentlab-decoders/blob/master/DL-PM/DL-PM.py
"""

import binascii
import datetime
import re
import struct
from typing import Optional
from zoneinfo import ZoneInfo

PROTOCOL_VERSION = 2

SENSORS = [
    {"length": 1, "values": [{"name": "Battery voltage", "convert": lambda x: x[0] / 1000, "unit": "V"}]},
    {
        "length": 10,
        "values": [
            {"name": "PM1.0 mass concentration", "convert": lambda x: x[0] / 10, "unit": "µg⋅m⁻³"},
            {"name": "PM2.5 mass concentration", "convert": lambda x: x[1] / 10, "unit": "µg⋅m⁻³"},
            {"name": "PM4 mass concentration", "convert": lambda x: x[2] / 10, "unit": "µg⋅m⁻³"},
            {"name": "PM10 mass concentration", "convert": lambda x: x[3] / 10, "unit": "µg⋅m⁻³"},
            {"name": "Typical particle size", "convert": lambda x: x[4], "unit": "nm"},
            {"name": "PM0.5 number concentration", "convert": lambda x: x[5] / 10},
            {"name": "PM1.0 number concentration", "convert": lambda x: x[6] / 10},
            {"name": "PM2.5 number concentration", "convert": lambda x: x[7] / 10},
            {"name": "PM4 number concentration", "convert": lambda x: x[8] / 10},
            {"name": "PM10 number concentration", "convert": lambda x: x[9] / 10},
        ],
    },
    {
        "length": 2,
        "values": [
            {"name": "Air temperature", "convert": lambda x: 175.72 * x[0] / 65536 - 46.85, "unit": "°C"},
            {"name": "Air humidity", "convert": lambda x: 125 * x[1] / 65536 - 6, "unit": "%"},
        ],
    },
    {"length": 1, "values": [{"name": "Barometric pressure", "convert": lambda x: x[0] * 2, "unit": "Pa"}]},
]


def decode(msg, hex_=False):
    """msg: payload as one of hex string, list, or bytearray"""
    bytes_ = bytearray(binascii.a2b_hex(msg) if hex_ else msg)
    version = bytes_[0]
    if version != PROTOCOL_VERSION:
        raise ValueError("protocol version {} doesn't match v2".format(version))

    devid = struct.unpack(">H", bytes_[1:3])[0]
    bin_flags = bin(struct.unpack(">H", bytes_[3:5])[0])
    flags = bin_flags[2:].zfill(struct.calcsize(">H") * 8)[::-1]

    words = [struct.unpack(">H", bytes_[i : i + 2])[0] for i in range(5, len(bytes_), 2)]

    cur = 0
    result = {"Device ID": devid, "Protocol version": version}
    for flag, sensor in zip(flags, SENSORS):
        if flag != "1":
            continue

        x = words[cur : cur + sensor["length"]]
        cur += sensor["length"]
        for value in sensor["values"]:
            if "convert" not in value:
                continue

            result[value["name"]] = {"value": value["convert"](x), "unit": value.get("unit", None)}
    return result


def clean_key(k):
    replace_re = re.compile(r"[. ]")
    new_key = replace_re.sub("_", k).lower()
    return new_key


def parse_decentlab_pm(hex_str: str, port: int) -> dict:
    """
    Use decode() to decode data from hex payload.
    Return decoded data in a dict.
    Replace [. ] with underscores in key names.
    """
    decoded = decode(hex_str, hex_=True)
    data = {}
    for k in decoded.keys():
        if isinstance(decoded[k], dict):
            data[clean_key(k)] = decoded[k]["value"]
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """Backwards compatibility function."""
    return parse_decentlab_pm(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "battery_voltage": 2.938,
          "air_temperature": 21.093493652343746,
          "air_humidity": 24.69305419921875,
          "barometric_pressure": 100178
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
                print(json.dumps(create_datalines(s[0], s[1], now), indent=2))
            except ValueError as err:
                print(f"Invalid FPort '{s[1]}' or payload size {len(s[0])}: {err}")
        print(f"\nUsage: {sys.argv[0]} hex_payload port\n\n")


if __name__ == "__main__":
    import json
    import sys

    examples = [
        ("022590000d0c4968bf5b2cc433", 1),  # Real data
        ("02258e000d0c2c68de5badc434", 1),  # Real data
        ("02258e000d0c2b69615c4cc452", 1),  # Real data
        ("022308000d0bd0689d5c74c401", 1),  # Real data
        ("022590000d0bdb62b23fa0c419", 1),  # Real data
    ]
    main(examples)
