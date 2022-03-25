"""
Parser for Digital Matter's Sensornode data format
https://digmat.freshdesk.com/helpdesk/attachments/16046195706
"""
import datetime
import struct
from typing import Optional
from zoneinfo import ZoneInfo

SENSORNODE_CSV = """ID;Table;Name;Size;Units
1;;System Firmware version (reset message);4;Struct
10;;GPS Position;6;Struct
20;batt;Battery Voltage;2;UINT16 (mV)
21;analog1;Analog In 1;2; UINT16 (mV)
22;analog2;Analog In 2;2; UINT16 (mV)
23;analog3;Analog In 3;2; UINT16 (mV)
30;digin1;Digital Input State;1;Bitfield
31;pulse1;Input 1 Pulse Count;2;UINT16
32;pulse2;Input 2 Pulse Count;2;UINT16
33;pulse3;Input 3 Pulse Count;2;UINT16
40;temp_in;Internal Temperature;2;INT16 (x100 degC)
41;temp_out1;Digital Matter I2C Temperature Probe 1 (Red);2;INT16 (x100 degC)
42;temp_out2;Digital Matter I2C Temperature Probe 2 (Blue);2;INT16 (x100 degC)
43;;Digital Matter I2C Temperature & Relative Humidity;3;Struct
50;battused;Battery Energy Used Since Power Up. 65535 = Unknown;2;UINT16 (mAh)
51;battleft;Estimated Battery % Remaining. 255 = Unknown;1;BYTE (0.5%)
"""


def parse_sensornode_table() -> dict:
    """
    Take in Sensornode field id and name mapping CSV and return it as a dict.
    """
    lines = SENSORNODE_CSV.splitlines()
    lines.pop(0)
    sensornode_map = {}
    for l in lines:
        c = l.split(";")
        if len(c) == 5:
            sensornode_map[int(c[0])] = {"table": c[1], "name": c[2], "size": int(c[3]), "type": c[4].split(" ")[0]}
    return sensornode_map


def parse_sensornode(hex_str: str, port: int) -> dict:
    """
    Decode Sensor node hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    _id = port
    tab = parse_sensornode_table()
    data = {}
    while len(hex_str) >= 0:
        t = tab[_id]
        s = t["size"] * 2  # Remove bytes * 2 because of hex format
        # Remove next chunk from hex payload
        chunk = hex_str[:s]
        hex_str = hex_str[s:]
        if _id in [1]:  # List contains fields not to parse
            # Get and remove next id from hex payload
            _id = int(hex_str[:2], 16)
            hex_str = hex_str[2:]
            continue
        x = bytes.fromhex(chunk)
        if _id in [10] and x[0] != 255:  # GPS data with fix

            def convert_deg(b):
                return int.from_bytes(b, byteorder="little", signed=True) / 10 ** 7 * 256.0

            data["lat"], data["lon"] = convert_deg(x[0:3]), convert_deg(x[3:6])
        if _id in [20, 21, 22, 23]:  # mV
            data[t["table"]] = struct.unpack("<H", x)[0] / 1000
        if _id in [30, 31, 32, 33]:  # count
            data[t["table"]] = struct.unpack("<H", x)[0]
        if _id in [40, 41, 42]:  # °C * 100
            data[t["table"]] = struct.unpack("<h", x)[0] / 100
        if _id in [43]:  # temp & humidity
            data["temprh_temp"] = struct.unpack("<h", x[:2])[0] / 100
            data["temprh_rh"] = x[2] / 2
        if len(hex_str) == 0:
            break
        _id = int(hex_str[:2], 16)
        hex_str = hex_str[2:]
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    return parse_sensornode(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "batt": 4.756,
          "temp_in": 4.42,
          "temp_out1": 3.43
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
        ["01e32337f80e14941228ba01295701", 10],
        ["ffffffffffff2b840846299108143414", 10],
        ["0d0016090028b30b143414", 21],
    ]
    main(examples)
