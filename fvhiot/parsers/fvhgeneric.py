"""
Parser for Forum Virium Helsinki's fvhgeneric data format.
Check internal documentation for now.
TODO: add documentation to here too.
"""

import datetime
from typing import Optional
from zoneinfo import ZoneInfo


FVHGENERIC_CSV = """ID;Table;Name;Size;Units
10;;GPS Position;6;Struct
20;epoch;Epoch timestamp;4;UINT16
80;button0;Button 0;1;UINT8
"""


def parse_fvhgeneric_table() -> dict:
    """
    Take in fvhgeneric field id and name mapping CSV and return it as a dict.
    """
    lines = FVHGENERIC_CSV.splitlines()
    lines.pop(0)
    fvhgeneric_map = {}
    for line in lines:
        c = line.split(";")
        if len(c) == 5:
            fvhgeneric_map[int(c[0])] = {"table": c[1], "name": c[2], "size": int(c[3]), "type": c[4].split(" ")[0]}
    return fvhgeneric_map


def parse_fvhgeneric(hex_str, port=None) -> dict:
    """
    Decode FVH's generic  hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """

    tab = parse_fvhgeneric_table()
    data = {}
    while len(hex_str) >= 0:
        id_ = int(hex_str[:2], 16)
        t = tab[id_]
        s = t["size"] * 2  # Remove bytes * 2 because of hex format
        # Remove next chunk from hex payload
        chunk = hex_str[2 : s + 2]
        hex_str = hex_str[s + 2 :]
        x = bytes.fromhex(chunk)
        if id_ in [10] and x[0] != 255:  # GPS data with fix

            def convert_deg(b):
                return int.from_bytes(b, byteorder="little", signed=True) / 10**7 * 256.0

            data["lat"], data["lon"] = convert_deg(x[0:3]), convert_deg(x[3:6])
        elif id_ in [20]:
            b = bytearray.fromhex(chunk)
            data["epoch"] = int.from_bytes(b, byteorder="little", signed=True)
        elif 80 <= id_ <= 89:  # buttons, id 80-89
            nr = id_ % 10  # 0-9
            data[f"button{nr}"] = int(chunk, 16)
        else:
            pass
        if len(hex_str) == 0:
            break
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    return parse_fvhgeneric(hex_str, port=port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "lat": 60.1993216,
          "lon": 25.0742016,
          "epoch": 1649924355,
          "button0": "10101010"
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
        ("0aa6e12307f20e1483cc57625010", 0),
        ("0aaae12306f20e14f5d757625001", 0),  # button 1
        ("0ab0e12300f20e143dd857625002", 0),  # button 2
        ("0ab3e12305f20e1487d857625004", 0),  # button 3
        ("0ab0e12305f20e1403d9576250aa", 0),  # button 2,4,6,8
    ]
    main(examples)
