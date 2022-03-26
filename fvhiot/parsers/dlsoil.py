"""
https://www.decentlab.com/products/soil-moisture-temperature-and-electrical-conductivity-sensor-for-lorawan
https://github.com/decentlab/decentlab-decoders/blob/master/DL-TRS12/DL-TRS12.py
"""
import binascii
import datetime
import re
import struct
from typing import Optional
from zoneinfo import ZoneInfo

PROTOCOL_VERSION = 2

SENSORS = [
    {
        "length": 3,
        "values": [
            {
                "name": "Dielectric permittivity",
                "convert": lambda x: pow(
                    0.000000002887 * pow(x[0] / 10, 3) - 0.0000208 * pow(x[0] / 10, 2) + 0.05276 * (x[0] / 10) - 43.39,
                    2,
                ),
            },
            {"name": "Volumetric water content", "convert": lambda x: x[0] / 10 * 0.0003879 - 0.6956, "unit": "m³⋅m⁻³"},
            {"name": "Soil temperature", "convert": lambda x: (x[1] - 32768) / 10, "unit": "°C"},
            {"name": "Electrical conductivity", "convert": lambda x: x[2], "unit": "µS⋅cm⁻¹"},
        ],
    },
    {"length": 1, "values": [{"name": "Battery voltage", "convert": lambda x: x[0] / 1000, "unit": "V"}]},
]


def decode(msg, hex_=False):
    """
    msg: payload as one of hex string, list, or bytearray

    return:

    {
     "Device ID": 4838,
     "Protocol version": 2,
     "Dielectric permittivity": {
      "value": 1.0392113047231324,
      "unit": null
     },
     "Volumetric water content": {
      "value": 0.002387260000000002,
      "unit": "m\u00b3\u22c5m\u207b\u00b3"
     },
     "Soil temperature": {
      "value": 20.6,
      "unit": "\u00b0C"
     },
     "Electrical conductivity": {
      "value": 0,
      "unit": "\u00b5S\u22c5cm\u207b\u00b9"
     },
     "Battery voltage": {
      "value": 3.037,
      "unit": "V"
     }
    }
    """
    bytes_ = bytearray(binascii.a2b_hex(msg) if hex_ else msg)
    version = bytes_[0]
    if version != PROTOCOL_VERSION:
        raise ValueError("protocol version {} doesn't match v2".format(version))

    devid = struct.unpack(">H", bytes_[1:3])[0]
    bin_flags = bin(struct.unpack(">H", bytes_[3:5])[0])
    flags = bin_flags[2:].zfill(struct.calcsize(">H") * 8)[::-1]

    words = [struct.unpack(">H", bytes_[i: i + 2])[0] for i in range(5, len(bytes_), 2)]

    cur = 0
    result = {"Device ID": devid, "Protocol version": version}
    for flag, sensor in zip(flags, SENSORS):
        if flag != "1":
            continue

        x = words[cur: cur + sensor["length"]]
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


def parse_decentlab_soil(hex_str: str, port: int):
    decoded = decode(hex_str, hex_=True)
    data = {}
    for k in decoded.keys():
        if isinstance(decoded[k], dict):
            data[clean_key(k)] = decoded[k]["value"]
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """Backwards compatibility function."""
    return parse_decentlab_soil(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "dielectric_permittivity": 56.07029496073391,
          "volumetric_water_content": 0.56519137,
          "electrical_conductivity": 1935,
          "temp_soil": 1.6,
          "batt": 2.924
        }
      }
    ]
    """
    values = parse_decentlab_soil(hex_str, port)
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
        ("0212e700037ef78010078f0b6c", 1),  # Real data
        ("0212e700037edb8011077f0b6c", 1),  # Real data
        ("0212e6000383f6802501360ae8", 1),  # Real data
        ("0212e60003840d801d01400ada", 1),  # Real data
    ]
    main(examples)
