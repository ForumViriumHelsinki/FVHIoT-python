import datetime
from zoneinfo import ZoneInfo
from typing import Optional


def get_value(hex_str: str, data: dict):
    if hex_str[:2] == "01":
        end = 6
        data["temp"] = int(hex_str[2:end], 16) / 10
        hex_str = hex_str[end:]
    if hex_str[:2] == "02":
        end = 4
        data["humi"] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    if hex_str[:2] == "04":
        end = 6
        data["lux"] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    if hex_str[:2] == "05":
        end = 4
        data["motion"] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    if hex_str[:2] == "06":
        end = 6
        data["co2"] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    if hex_str[:2] == "07":
        end = 6
        data["volt"] = int(hex_str[2:end], 16) / 1000
        hex_str = hex_str[end:]
    else:
        data["error"] = hex_str
        hex_str = ""
    return hex_str, data


def parse_elsys(hex_str: str, port: int = None):
    """
    Parse payload like "01010f022e04006605000601b6070e4e".
    See online converter: https://www.elsys.se/en/elsys-payload/
    And document "Elsys LoRa payload_v10" at https://www.elsys.se/en/lora-doc/
    :param hex_str: ELSYS hex payload
    :param port: LoRaWAN port
    :return: dict containing float values
    """
    data = {}
    # This while loop is just in case here, get_value seems to parse all values
    # when they are in numeric order (01, 02, 04, 05, 06, 07)
    while len(hex_str) > 0:
        hex_str, data = get_value(hex_str, data)
    return data


def decode_hex(hex_str: str, port: int = None):
    return parse_elsys(hex_str, port=port)


def create_datalines(hex_str: str, time_str: Optional[str] = None, port: Optional[int] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.

    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "temp": 25.8,
          "humi": 47,
          "lux": 0,
          "motion": 0,
          "co2": 629,
          "volt": 3.663
        }
      }
    ]
    """
    values = decode_hex(hex_str, port)
    dataline = {"time": time_str, "data": values}
    datalines = [dataline]
    return datalines


if __name__ == "__main__":
    import sys

    now = datetime.datetime(2022, 3, 2, 12, 21, 30, 123000, tzinfo=ZoneInfo("UTC")).isoformat()
    try:
        print(parse_elsys(sys.argv[1], int(sys.argv[2])))
    except IndexError as err:
        print("Some examples:")
        for s in [
            ("010112022d0400f20504060140070e51", 5),
            ("010109022f0400000500060224070e38", 5),
            ("010102022f0400000500060275070e4f", 5),
        ]:
            print(create_datalines(s[0], time_str=now, port=s[1]))

        print(f"\nUsage: {sys.argv[0]} hex_payload port\n\n")
