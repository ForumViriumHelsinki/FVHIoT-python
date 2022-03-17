"""
Parser for one of these: https://ekoenergetyka.com.pl/products/

Data comes nicely in json, so not much to do...
"""
import json

from typing import Optional, Union, Any


def parse_ekoevcharging():
    pass


def decode_payload(payload: Union[str, Any]):
    if isinstance(payload, str):
        return json.load(payload)
    else:
        return payload


def create_datalines(decode_value: str, time_str: Optional[str] = None) -> list:
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
    values = decode_payload(decode_value)
    dataline = {"time": time_str, "data": values}
    datalines = [dataline]
    return datalines
