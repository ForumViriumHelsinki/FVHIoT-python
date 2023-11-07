"""
SenseCAP Sensornode / sompameter decoder. See:
https://github.com/sompasauna/sompis-metering-firmware
"""

import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from ..utils.lorawan.thingpark import get_uplink_obj


def parse_s_sensecap(payload_hex: str, port: int) -> dict:
    """
    Actual measurements come n 3 packages '30' first, '32' middle and '33' last
    Note: middle packet is one byte shorter form other packets
    """
    bytebuffer = bytearray.fromhex(payload_hex)
    data = dict()
    while len(bytebuffer) >= 10:
        _id = bytebuffer[0]
        if _id == 0x30:
            db = bytebuffer[:11]
            bytebuffer = bytebuffer[11:]
            data["temperature_sht_c"] = int.from_bytes(db[3:7], byteorder="big", signed=True) / 1000000
            data["humidity_sht"] = int.from_bytes(db[7:], byteorder="big", signed=True) / 1000000
        elif _id == 0x32:
            db = bytebuffer[:10]
            bytebuffer = bytebuffer[10:]
            data["temperature_ath_c"] = int.from_bytes(db[2:6], byteorder="big", signed=True) / 1000
            data["humidity_ath"] = int.from_bytes(db[6:], byteorder="big", signed=True) / 1000
        elif _id == 0x33:
            db = bytebuffer[:11]
            bytebuffer = bytebuffer[11:]
            data["temperature_mcp"] = int.from_bytes(db[3:7], byteorder="big", signed=True) / 1000000
            data["ref_temperature_mcp"] = int.from_bytes(db[7:], byteorder="big", signed=True) / 1000000
        elif _id == 0x39:
            db = bytebuffer[:11]
            bytebuffer = bytebuffer[11:]
            data["battery_percentage"] = db[1]
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    NOTE: this is here for backwards compatibility.
    """
    return parse_s_sensecap(hex_str, port)


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
        "time": "2023-06-26T06:39:21.061321+00:00",
        "data": {
          "temperature_sht_c": 25.83,
          "humidity_sht": 46.53,
          "temperature_ath_c": 25.0,
          "humidity_ath": 47.0,
          "temperature_mcp": 25.5,
          "ref_temperature_mcp": 25.5
        }
      }
    ]
    """
    values = decode_hex(hex_str, port)
    dataline = {"time": time_str, "data": values}
    datalines = [dataline]
    return datalines


def main(samples: list):
    now = datetime.datetime.now(tz=ZoneInfo("UTC")).isoformat()
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
        ("301203018a227002c5fdd03234000061a80000b7983356030185196001851960", "3"),
        ("301203018a97a002c6c1203234000061a80000b7983356030183311801851960", "3"),
        ("301203018a97a002c5fdd0", "3"),
        ("3234000061a80000b798", "3"),
        ("3356030183311801851960", "3"),
        ("39600101000200050000", "3"),  # battery status
        ("3402000100", "3"),  # status package not documented so ignore
    ]
    main(examples)
