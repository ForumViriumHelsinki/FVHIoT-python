"""
Paxcounter parser
"""

import datetime
from typing import Optional
from zoneinfo import ZoneInfo


"""
See example here:
https://github.com/cyberman54/ESP32-Paxcounter/blob/master/src/TTN/plain_decoder.js
"""


def parse_paxcounter(payload_hex: str, port: int) -> dict:
    """
    Extract wifi and ble counts from `payload_hex` and return them in a dict.
    Currently, only payloads sent to FPort 1 are parsed and FPort 9 are ignored.
    Raise ValueError, if different port is used or payload size differs from 4 or 8.
    """
    data = {}
    if int(port) == 1:
        payload_len = len(payload_hex)
        # We assume here PAXCOUNTER is configured to send data in "plain" format
        # paxcounter.conf: #define PAYLOAD_ENCODER                 1
        if payload_len == 4:
            data["wifi"] = int(payload_hex[0:4], 16)
        elif payload_len == 8:
            data["wifi"] = int(payload_hex[0:4], 16)
            data["ble"] = int(payload_hex[4:8], 16)
        else:
            raise ValueError(f"Payload with size {payload_len} is not currently supported.")
    elif int(port) == 9:
        return data
    else:
        raise ValueError(f"Port '{port}' is not currently supported.")
    # TODO: Other ports and payload formats are not implemented yet
    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    NOTE: this is here for backwards compatibility.
    """
    return parse_paxcounter(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "wifi": 3,
          "ble": 4
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
        ("00020001", 1),
        ("0003", 1),
        ("fa117415aaaa", 1),  # Fails
        ("0d00", 2),  # Fails
        ("ff", 9),  # Ignored
        ("0d0016090028b30b143414", 21),  # Fails
    ]
    main(examples)
