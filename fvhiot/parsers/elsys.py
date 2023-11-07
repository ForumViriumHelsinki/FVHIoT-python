"""
Check https://www.elsys.se/en/elsys-payload/ for javascript decoder.
"""

import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from ..utils.lorawan.thingpark import get_uplink_obj

id_name_map = {
    "01": "temp",  # temp 2 bytes -3276.8°C -->3276.7°C
    "02": "rh",  # Humidity 1   0-100%
    "03": "acc",  # acceleration 3 bytes X,Y,Z -128 --> 127 +/-63=1G
    "04": "light",  # Light 2 bytes 0-->65535 Lux
    "05": "motion",  # No of motion 1 byte 0-255
    "06": "co2",  # Co2 2 bytes 0-65535 ppm
    "07": "vdd",  # VDD 2byte 0-65535mV
    "08": "analog1",  # VDD 2byte 0-65535mV
    "09": "gps",  # 3bytes lat 3bytes long binary
    "0a": "pulse1",  # 2bytes relative pulse count
    "0b": "pulse1_abs",  # 4bytes no 0->0xFFFFFFFF
    "0c": "ext_temp1",  # 2bytes -3276.5C-->3276.5C
    "0d": "ext_digital",  # 1bytes value 1 or 0
    "0e": "ext_distance",  # 2bytes distance in mm
    "0f": "acc_motion",  # 1byte number of vibration/motion
    "10": "ir_temp",  # 2bytes internal temp 2bytes external temp -3276.5C-->3276.5C
    "11": "occupancy",  # 1byte data
    "12": "waterleak",  # 1byte data 0-255
    "13": "grideye",  # 65byte temperature data 1byte ref+64byte external temp
    "14": "pressure",  # 4byte pressure data (hPa)
    "15": "sound",  # 2byte sound data (peak/avg)
    "16": "pulse2",  # 2bytes 0-->0xFFFF
    "17": "pulse2_abs",  # 4bytes no 0->0xFFFFFFFF
    "18": "analog2",  # 2bytes voltage in mV
    "19": "ext_temp2",  # 2bytes -3276.5C-->3276.5C
    "1a": "ext_digital2",  # 1bytes value 1 or 0
    "1b": "ext_analog_uv",  # 4 bytes signed int (uV)
    "1c": "tvoc",  # 2 bytes (ppb)
    "3d": "debug",  # 4bytes debug
}


def get_value(hex_str: str, data: dict):
    _id = hex_str[:2]
    if _id == "01":
        end = 6
        data[id_name_map[_id]] = int(hex_str[2:end], 16) / 10
        hex_str = hex_str[end:]
    elif _id == "02":
        end = 4
        data[id_name_map[_id]] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    elif _id == "04":
        end = 6
        data[id_name_map[_id]] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    elif _id == "05":
        end = 4
        data[id_name_map[_id]] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    elif _id == "06":
        end = 6
        data[id_name_map[_id]] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    elif _id == "07":
        end = 6
        data[id_name_map[_id]] = int(hex_str[2:end], 16) / 1000
        hex_str = hex_str[end:]
    elif _id == "15":
        end = 6
        data["sound_peak"] = int(hex_str[2:4], 16)
        data["sound_avg"] = int(hex_str[4:6], 16)
        hex_str = hex_str[end:]
    else:
        data["error"] = hex_str
        hex_str = ""
    return hex_str, data


def parse_elsys(hex_str: str, port: int):
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


def decode_hex(hex_str: str, port: int):
    return parse_elsys(hex_str, port)


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
        ("010112022d0400f20504060140070e51", 5),
        ("010109022f0400000500060224070e38", 5),
        ("010102022f0400000500060275070e4f", 5),
        ("010107021704002705020601b0070e4e", 5),
        ("010031025404073c0500070e0b154f37", 5),
    ]
    main(examples)
