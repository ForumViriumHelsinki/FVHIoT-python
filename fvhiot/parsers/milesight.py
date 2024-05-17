"""
Parser for Milesight-EM300-TH data format
https://github.com/Milesight-IoT/SensorDecoders/blob/main/EM_Series/EM300_Series/EM300-TH/EM300-TH_Decoder.js
"""
import datetime
import struct
from typing import Optional
from zoneinfo import ZoneInfo


def read_uint16_le(bytes):
    return struct.unpack("<H", bytes)[0]


def read_int16_le(bytes):
    return struct.unpack("<h", bytes)[0]


def read_uint32_le(bytes):
    return struct.unpack("<I", bytes)[0]


def parse_milesight(hex_str: str, port: int) -> dict:
    """
    Decode Milesight hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    byte_data = bytes.fromhex(hex_str)
    data = {}
    if port != 85:
        return data
    i = 0
    while i < len(byte_data):
        channel_id = byte_data[i]
        channel_type = byte_data[i + 1]
        i += 2

        if channel_id == 0x01 and channel_type == 0x75:
            data["battery"] = byte_data[i]
            i += 1
        elif channel_id == 0x03 and channel_type == 0x67:
            data["temperature"] = read_int16_le(byte_data[i: i + 2]) / 10.0
            i += 2
        elif channel_id == 0x04 and channel_type == 0x68:
            data["humidity"] = byte_data[i] / 2.0
            i += 1
        elif channel_id == 0x20 and channel_type == 0xCE:
            point = {}
            point["timestamp"] = read_uint32_le(byte_data[i: i + 4])
            point["temperature"] = read_int16_le(byte_data[i + 4: i + 6]) / 10.0
            point["humidity"] = byte_data[i + 6] / 2.0
            if "history" not in data:
                data["history"] = []
            data["history"].append(point)
            i += 8
        else:
            break

    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    return parse_milesight(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.
    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "battery": 100,
          "temperature": 24.5,
          "humidity": 51.0
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
        ["0367e70004684d", 85],
        ["0367ed0004684b", 85],
        ["0367f100046847", 85],
        ["0175640367f500046866", 85],
    ]
    main(examples)
