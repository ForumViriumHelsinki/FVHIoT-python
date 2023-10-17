"""
# Parser for IoTPetri's modified paxcounter data format.
https://bitbucket.org/iotpetri/public_petris/src/master/ESP32/LoRa/ESP32_PAX_COUNTER_WITH_LORA_MPC1700_V2022-05/

## Lora Payload new 1.6.2022

```
Payload: 0-6 BYTE
Data (hex): 69 13 AA 4 AA 1A AA

BYTE 0 (12-14) battery level: 0x69
BYTE 1-2 (15-16) BLE scan count: 0x13AA
BYTE 3-4 (17-18) BLE new : 0x04AA
BYTE 5-6 (19-20) BLE staying: 0x1AAA
```

## Lora Payload Battery lever scaling back to normal

```
HEX 57 = DEC 87
Scale Factor = 8
Start Voltage (mv) = 2500
87 * 8 +2500 = 3196
```
"""

import datetime
from typing import Optional
from zoneinfo import ZoneInfo
from ..utils.lorawan.thingpark import get_uplink_obj


def parse_paxcounter(hex_str: str, port: int) -> dict:
    """
    Decode IoTPetri's paxcounter hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    data = {}
    batt_raw = int(hex_str[:2], 16)
    data["batt"] = batt_raw * 8 + 2500
    if len(hex_str) > 2:
        data["ble_count"] = int(hex_str[2:6], 16)
        data["ble_new"] = int(hex_str[6:10], 16)
        data["ble_stay"] = int(hex_str[10:14], 16)
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    return parse_paxcounter(hex_str, port)


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
          "batt": 3204,
          "ble_count": 4,
          "ble_new": 1,
          "ble_stay": 12
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
        ["58000b0000002d", 1],  # example data
        ["58000a0000002a", 1],  # example data
        ["58000c00020027", 1],  # example data
        ["58000b00000025", 1],  # example data
        ["58000b00000021", 1],  # example data
        ["5800040001000c", 1],  # example data
        ["58", 1],  # example data, battery empty
        ["57", 1],  # example data, battery empty
    ]
    main(examples)
