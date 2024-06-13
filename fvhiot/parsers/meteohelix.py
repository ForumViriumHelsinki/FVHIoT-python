"""
Parser for Meteohelix weather sation data format.

Converting payload hex to decimal

    Meteohelix decode
    Payload sample: "6F19C10A393F28B00601FF"

    Type = 2 first bits
    Battery = 5 next bits *0.05+3
    Temperature = 11 bits *0.1-100
    T_min = 6 bits Temperature - T_min *0.1
    T_max = 6 bits Temperature + T_max *0.1
    Humidity = 9 bits *0.2
    Pressure = 14 bits *5+50000
    Irradiation = 10 bits *2
    Irr_max = Irradiation + 9 bits *2
    Rain = 8 bits ( not used )
    Rain_min_time = 8 bits ( not used )
"""

import datetime
from typing import Optional
from zoneinfo import ZoneInfo


def parse_meteohelix(hex_str: str, port: int) -> dict:
    """
    Decode Sensor node hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    numero = int(hex_str, 16)
    bittitaulukko = bin(numero)[2:]
    battery = int(bittitaulukko[1:6], 2) * 0.05 + 3
    temperature = round(int(bittitaulukko[6:17], 2) * 0.1 - 100, 1)
    t_min = round(temperature - int(bittitaulukko[17:23], 2) * 0.1, 1)
    t_max = round(temperature + int(bittitaulukko[23:29], 2) * 0.1, 1)
    humidity = round(int(bittitaulukko[29:38], 2) * 0.2, 1)
    pressure = (int(bittitaulukko[38:52], 2) * 5 + 50000) / 100
    irradiation = int(bittitaulukko[52:62], 2) * 2
    irr_max = irradiation + int(bittitaulukko[52:61], 2) * 2

    data = {
        "battery": battery,
        "temperature": temperature,
        "t_min": t_min,
        "t_max": t_max,
        "humidity": humidity,
        "pressure": pressure,
        "irradiation": irradiation,
        "irr_max": irr_max,
    }

    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    NOTE: this is here for backwards compatibility.
    """

    return parse_meteohelix(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
        Return well-known parsed data formatted list of data, e.g.

    [
        {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "battery": 4.15,
          "temperature": 12.7,
          "t_min": 12.6,
          "t_max": 12.9,
          "humidity": 56.8,
          "pressure": 1010.65,
          "irradiation": 176,
          "irr_max": 264
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
        ("6F19C10A393F28B00601FF", 1),
    ]
    main(examples)
