"""
Sample return value for create_datalines():

[
  {
    "time": "2021-02-18T14:54:36+00:00",
    "data": {
      "temp": -9.56,
      "humi": 89.5,
      "pres": 1025.0
    }
  },
  {
    "time": "2021-02-18T15:24:40+00:00",
    "data": {
      "temp": -9.64,
      "humi": 91.0,
      "pres": 1024.87
    }
  },
  {
    "time": "2021-02-18T15:54:46+00:00",
    "data": {
      "temp": -9.9,
      "humi": 91.5,
      "pres": 1024.46
    }
  }
]
"""

import datetime
import struct
from typing import Optional
from zoneinfo import ZoneInfo


def extract_bits(value: int, first: int, last: int) -> int:
    """
    Extract some bits from int `value`
    """
    value >>= first
    mask = ~((-1) << (last - first + 1))
    return value & mask


def get_timestamp(value: bytes) -> datetime.datetime:
    """
    Extract timezone aware datetime from mcf88 measurement.
    `value` is the measurement converted to bytes.
    """
    (timestamp,) = struct.unpack("<I6x", value)
    year = extract_bits(timestamp, 25, 31) + 2000
    month = extract_bits(timestamp, 21, 24)
    day = extract_bits(timestamp, 16, 20)
    hour = extract_bits(timestamp, 11, 15)
    minute = extract_bits(timestamp, 5, 10)
    second = extract_bits(timestamp, 0, 4) * 2
    dt = datetime.datetime(year, month, day, hour, minute, second, tzinfo=ZoneInfo("UTC"))
    return dt


def parse_mcf88(hex_str: str, port=None) -> Optional[list]:
    """
    Parse MCF88 hex payload like
    "0462651527da078e4d8e01a4691527dd078f488e01676d1527e9078d1a8e015d" to float values.
    Note: LoRaWAN port is not used here.
    """
    if hex_str[:2] == "04":
        line = hex_str[2:62]
        n = 20
        datas = [line[i: i + n] for i in range(0, len(line), n)]
        datalines = []
        for data in datas:
            value = bytes.fromhex(data)
            ts = get_timestamp(value)  # datetime in UTC (timezone aware)
            parsed_data = {
                "temp": struct.unpack("<h", bytes.fromhex(data[8:12]))[0] / 100,  # °C
                "humi": int(data[12:14], 16) / 2,
                "pres": struct.unpack("<I", bytes.fromhex(data[14:20] + "00"))[0] / 100,  # hPa
            }
            # TODO: should we have create_dataline() function?
            # dataline = create_dataline(ts, parsed_data)
            # datalines.append(dataline)
            # TODO: should we pydantic model DataLine for this?
            dataline = {"time": ts.isoformat(), "data": parsed_data}
            datalines.append(dataline)
        # import json
        # print(json.dumps(datalines, indent=2))
        return datalines
    return None


def decode_hex(hex_str: str, port: int = None):
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    return parse_mcf88(hex_str, port=port)


def create_datalines(hex_str: str, time_str: Optional[str] = None, port: Optional[int] = None) -> list:
    """
    Return well-known parsed data formatted list of data.
    See an example in the header of this file or run this module.
    """
    return decode_hex(hex_str, port=port)


if __name__ == "__main__":
    import sys

    try:
        print(decode_hex(sys.argv[1], int(sys.argv[2])))
    except IndexError as err:
        print("Some examples:")
        for s in [
            ("04d276522a44fcb3649001147b522a3cfcb6579001d77e522a22fcb72e900152", 2),
            ("04bd79522a2ffcc8869001827d522a06fcc8549001c481522a12fcc84190015b", 2),
            ("042279522a68fca5489101e57c522a72fca62191012781522a6efca60691015c", 2),
        ]:
            print(create_datalines(s[0], port=s[1]))

        print(f"\nUsage: {sys.argv[0]} hex_payload port\n\n")
