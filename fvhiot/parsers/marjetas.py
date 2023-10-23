"""
Parser for Marjetas' Dropstick temperature sensor data format.
https://www.mtvuutiset.fi/artikkeli/suomalaisyrityksen-innovaatio-parantaisi-ajoturvallisuutta-talvikeleilla-kokeilut-ovat-olleet-uskomattoman-positiivisia/7812138#gs.v6amc4

Converting payload hex to decimal

"payload hex"; "aa083d08d107c407"-> aa08 3d08 d107 c407
aa08-> byte order little-endian-> 08aa (hex) = 2218 (decimal)-> 2218 / 100 = 22.18
3d08-> byte order little endian-> 083d (hex) = 2109 (decimal)-> 2109 / 100 = 21.09
d107-> byte order little endian-> 07d1 (hex) = 2001 (decimal)-> 2001 / 100 = 20.01
c407-> byte order little endian-> 07c4 (hex) = 1988 (decimal)-> 1988 / 100 = 19.88

"payload hex":"c8ffe7ffffff1700"-> c8ff e7ff ffff 1700
c8ff-> byte order little-endian-> ffc8 (hex) =-56 (decimal from signed 2's complement)->-56 / 100 =-0.56
e7ff-> byte order little-endian-> ffe7 (hex) =-25 (decimal from signed 2's complement)->-25 / 100 =-0.25
ffff-> byte order little-endian-> ffff (hex) =-1 (decimal from signed 2' s complement)->-1 / 100 =-0.01
1700-> byte order little-endian-> 0017 (hex) = 23 (decimal)-> 23 / 100 0.23
"""

import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from ..utils.lorawan.thingpark import get_uplink_obj


def parse_marjetas(hex_str: str, port: int) -> dict:
    """
    Decode Sensor node hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    data = {}
    n = 4
    temp_nro = 0
    for h4 in [hex_str[i : i + n] for i in range(0, len(hex_str), n)]:
        i = int(h4[2:4] + h4[0:2], 16)
        if i > int("7fff", 16):
            i = i - (int("ffff", 16) + 1)
        temp = i / 100
        data[f"temp_{temp_nro:02}"] = temp
        temp_nro += 1
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    return parse_marjetas(hex_str, port)


def create_datalines_from_raw_unpacked_data(unpacked_data: dict) -> list:
    """
    parse raw data from unpacked_data
    Return well-known parsed data formatted list of data and packet timestamp
    """
    uplink_obj = get_uplink_obj(unpacked_data)
    datalines = create_datalines(uplink_obj.payload_hex, port=uplink_obj.FPort, time_str=uplink_obj.Time)
    packet_timestamp = datetime.datetime.strptime(uplink_obj.Time, "%Y-%m-%dT%H:%M:%S.%f%z")

    return packet_timestamp, datalines


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "temp_00": -0.18,
          "temp_01": -0.31,
          "temp_02": 0.12,
          "temp_03": 1.93
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
        ["aa083d08d107c407", 2],  # example data
        ["c8ffe7ffffff1700", 2],  # example data
        ["3800250083008901", 2],  # real data
        ["90ffafffe1ffa200", 2],  # real data
        ["e7fff4ffe7ff7600", 2],  # real data
        ["eeffe1ff0c00c100", 2],  # real data
    ]
    main(examples)
