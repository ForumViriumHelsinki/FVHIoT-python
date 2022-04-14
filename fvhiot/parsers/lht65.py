"""
Dragino LHT65 parser

See example here:
https://www.dragino.com/downloads/downloads/LHT65/UserManual/LHT65_Temperature_Humidity_Sensor_UserManual_v1.3.pdf
"""
import datetime
from typing import Optional
from zoneinfo import ZoneInfo


def parse_lht65(payload_hex: str, port: int) -> dict:
    """
    Extract wifi and ble counts from `payload_hex` and return them in a dict.
    Currently, only payloads sent to FPort 1 are parsed.
    Raise ValueError, if different port is used or payload size differs from 4 or 8.
    """
    bytebuffer = bytearray.fromhex(payload_hex)
    data = dict(
        battery_v=((bytebuffer[0] << 8 | bytebuffer[1]) & 0x3FFF) / 1000,
        # SHT20 is in the box
        # temperature_sht_c=(bytebuffer[2] << 24 >> 16 | bytebuffer[3]) / 100,
        temperature_sht_c=((bytebuffer[2] << 8 | bytebuffer[3]) - (0xFFFF if bytebuffer[2] > 0x7F else 0)) / 100,
        humidity_sht=(bytebuffer[4] << 8 | bytebuffer[5]) / 10,
        # DS18B20 external probe
        # temperature_ds_c=(bytebuffer[7] << 24 >> 16 | bytebuffer[8]) / 100
        temperature_ds_c=((bytebuffer[7] << 8 | bytebuffer[8]) - (0xFFFF if bytebuffer[7] > 0x7F else 0)) / 100,
    )
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    NOTE: this is here for backwards compatibility.
    """
    return parse_lht65(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "battery_v": 2.947,
          "temperature_sht_c": 4.5,
          "humidity_sht": 84.1,
          "temperature_ds_c": 49.0
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
        ("cbb0018c02b1010f0a7fff", 2),
        ("cb8301c20345010e747fff", 2),
        ("cb8301c003470110cc7fff", 2),
        ("cbaf018a02b20110367fff", 2),
        ("cb8301c203490113247fff", 2),
    ]
    main(examples)
