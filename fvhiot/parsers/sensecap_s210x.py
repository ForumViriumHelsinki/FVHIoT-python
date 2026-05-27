"""SenseCAP S210X LoRaWAN payload decoder.

Python port of the official Seeed/SenseCAP JavaScript decoder.
Handles all S210X-series sensors (S2100, S2101, S2102, S2103, S2104, S2105, ...).
"""

from __future__ import annotations

import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

# CRC16 lookup table (CCITT, reflected). Copied verbatim from the JS reference.
_CRC16_TAB: tuple[int, ...] = (
    0x0000,
    0x1189,
    0x2312,
    0x329B,
    0x4624,
    0x57AD,
    0x6536,
    0x74BF,
    0x8C48,
    0x9DC1,
    0xAF5A,
    0xBED3,
    0xCA6C,
    0xDBE5,
    0xE97E,
    0xF8F7,
    0x1081,
    0x0108,
    0x3393,
    0x221A,
    0x56A5,
    0x472C,
    0x75B7,
    0x643E,
    0x9CC9,
    0x8D40,
    0xBFDB,
    0xAE52,
    0xDAED,
    0xCB64,
    0xF9FF,
    0xE876,
    0x2102,
    0x308B,
    0x0210,
    0x1399,
    0x6726,
    0x76AF,
    0x4434,
    0x55BD,
    0xAD4A,
    0xBCC3,
    0x8E58,
    0x9FD1,
    0xEB6E,
    0xFAE7,
    0xC87C,
    0xD9F5,
    0x3183,
    0x200A,
    0x1291,
    0x0318,
    0x77A7,
    0x662E,
    0x54B5,
    0x453C,
    0xBDCB,
    0xAC42,
    0x9ED9,
    0x8F50,
    0xFBEF,
    0xEA66,
    0xD8FD,
    0xC974,
    0x4204,
    0x538D,
    0x6116,
    0x709F,
    0x0420,
    0x15A9,
    0x2732,
    0x36BB,
    0xCE4C,
    0xDFC5,
    0xED5E,
    0xFCD7,
    0x8868,
    0x99E1,
    0xAB7A,
    0xBAF3,
    0x5285,
    0x430C,
    0x7197,
    0x601E,
    0x14A1,
    0x0528,
    0x37B3,
    0x263A,
    0xDECD,
    0xCF44,
    0xFDDF,
    0xEC56,
    0x98E9,
    0x8960,
    0xBBFB,
    0xAA72,
    0x6306,
    0x728F,
    0x4014,
    0x519D,
    0x2522,
    0x34AB,
    0x0630,
    0x17B9,
    0xEF4E,
    0xFEC7,
    0xCC5C,
    0xDDD5,
    0xA96A,
    0xB8E3,
    0x8A78,
    0x9BF1,
    0x7387,
    0x620E,
    0x5095,
    0x411C,
    0x35A3,
    0x242A,
    0x16B1,
    0x0738,
    0xFFCF,
    0xEE46,
    0xDCDD,
    0xCD54,
    0xB9EB,
    0xA862,
    0x9AF9,
    0x8B70,
    0x8408,
    0x9581,
    0xA71A,
    0xB693,
    0xC22C,
    0xD3A5,
    0xE13E,
    0xF0B7,
    0x0840,
    0x19C9,
    0x2B52,
    0x3ADB,
    0x4E64,
    0x5FED,
    0x6D76,
    0x7CFF,
    0x9489,
    0x8500,
    0xB79B,
    0xA612,
    0xD2AD,
    0xC324,
    0xF1BF,
    0xE036,
    0x18C1,
    0x0948,
    0x3BD3,
    0x2A5A,
    0x5EE5,
    0x4F6C,
    0x7DF7,
    0x6C7E,
    0xA50A,
    0xB483,
    0x8618,
    0x9791,
    0xE32E,
    0xF2A7,
    0xC03C,
    0xD1B5,
    0x2942,
    0x38CB,
    0x0A50,
    0x1BD9,
    0x6F66,
    0x7EEF,
    0x4C74,
    0x5DFD,
    0xB58B,
    0xA402,
    0x9699,
    0x8710,
    0xF3AF,
    0xE226,
    0xD0BD,
    0xC134,
    0x39C3,
    0x284A,
    0x1AD1,
    0x0B58,
    0x7FE7,
    0x6E6E,
    0x5CF5,
    0x4D7C,
    0xC60C,
    0xD785,
    0xE51E,
    0xF497,
    0x8028,
    0x91A1,
    0xA33A,
    0xB2B3,
    0x4A44,
    0x5BCD,
    0x6956,
    0x78DF,
    0x0C60,
    0x1DE9,
    0x2F72,
    0x3EFB,
    0xD68D,
    0xC704,
    0xF59F,
    0xE416,
    0x90A9,
    0x8120,
    0xB3BB,
    0xA232,
    0x5AC5,
    0x4B4C,
    0x79D7,
    0x685E,
    0x1CE1,
    0x0D68,
    0x3FF3,
    0x2E7A,
    0xE70E,
    0xF687,
    0xC41C,
    0xD595,
    0xA12A,
    0xB0A3,
    0x8238,
    0x93B1,
    0x6B46,
    0x7ACF,
    0x4854,
    0x59DD,
    0x2D62,
    0x3CEB,
    0x0E70,
    0x1FF9,
    0xF78F,
    0xE606,
    0xD49D,
    0xC514,
    0xB1AB,
    0xA022,
    0x92B9,
    0x8330,
    0x7BC7,
    0x6A4E,
    0x58D5,
    0x495C,
    0x3DE3,
    0x2C6A,
    0x1EF1,
    0x0F78,
)

# DataID -> human-readable measurement name.
# IDs > 4096 are telemetry; lower IDs are control/metadata frames.
_MEASUREMENT_NAMES: dict[int, str] = {
    4097: "air_temperature",
    4098: "air_humidity",
    4099: "light_intensity",
    4100: "co2",
    4101: "barometric_pressure",
    4102: "soil_temperature",
    4103: "soil_moisture",
    4104: "wind_direction",
    4105: "wind_speed",
    4106: "ph",
    4107: "light_quantum",
    4108: "electrical_conductivity",
    4109: "dissolved_oxygen",
    4110: "soil_volumetric_water_content",
    4111: "soil_electrical_conductivity",
    4112: "soil_temperature_vwc_ec",
    4113: "rainfall_hourly",
    4115: "distance",
    4116: "water_leak",
    4117: "liquid_level",
    4118: "nh3",
    4119: "h2s",
    4120: "flow_rate",
    4121: "total_flow",
    4122: "oxygen_concentration",
    4123: "water_electrical_conductivity",
    4124: "water_temperature",
    4125: "soil_heat_flux",
    4126: "sunshine_duration",
    4127: "total_solar_radiation",
    4128: "water_surface_evaporation",
    4129: "par",
    4130: "accelerometer",
    4131: "volume",
    4133: "soil_tension",
    4134: "salinity",
    4135: "tds",
    4136: "leaf_temperature",
    4137: "leaf_wetness",
    4138: "soil_moisture_10cm",
    4139: "soil_moisture_20cm",
    4140: "soil_moisture_30cm",
    4141: "soil_moisture_40cm",
    4142: "soil_temperature_10cm",
    4143: "soil_temperature_20cm",
    4144: "soil_temperature_30cm",
    4145: "soil_temperature_40cm",
    4146: "pm2_5",
    4147: "pm10",
    4148: "noise",
    4150: "accelerometer_x",
    4151: "accelerometer_y",
    4152: "accelerometer_z",
    4175: "ai_detection_01",
    4176: "ai_detection_02",
    4177: "ai_detection_03",
    4178: "ai_detection_04",
    4179: "ai_detection_05",
    4180: "ai_detection_06",
    4181: "ai_detection_07",
    4182: "ai_detection_08",
    4183: "ai_detection_09",
    5100: "switch",
}

_SPECIAL_IDS: frozenset[int] = frozenset({0, 1, 2, 3, 4, 7, 9, 0x120})


def _crc16_check(payload: bytes) -> bool:
    """Validate the trailing CRC16 over the full payload.

    The SenseCAP CRC is computed such that running the algorithm over
    payload + CRC yields 0 when the CRC is correct.
    """
    crc = 0
    for byte in payload:
        crc = (crc >> 8) ^ _CRC16_TAB[(crc ^ byte) & 0xFF]
    return crc == 0


def _decode_signed_le_4bytes(chunk: bytes) -> float:
    """Decode 4 little-endian bytes as a signed int, scaled by 1/1000.

    This is the default scaling used by all telemetry measurements.
    """
    value = int.from_bytes(chunk, byteorder="little", signed=True)
    return value / 1000.0


def _decode_special(data_id: int, chunk: bytes) -> Any:
    """Decode the 4-byte value field for control/metadata frames."""
    # Sensor EUI halves: keep as upper-case hex, big-endian display order.
    if data_id in (2, 3):
        return chunk[::-1].hex().upper()

    # Version frames: two 16-bit words, each rendered as "major.minor".
    if data_id in (0, 1):
        reversed_bytes = chunk[::-1]
        parts = []
        for i in (0, 2):
            major = reversed_bytes[i]
            minor = reversed_bytes[i + 1]
            parts.append(f"{major}.{minor}")
        return ",".join(parts)

    # Timestamp-ish 4-byte BCD/decimal (data_id 4): each byte printed as 2 digits.
    if data_id == 4:
        reversed_bytes = chunk[::-1]
        return "".join(f"{b:02d}" for b in reversed_bytes)

    # Battery (lower 16 bits, %) and uplink interval (upper 16 bits, minutes).
    # NOTE: matches the JS implementation's layout after little-endian reversal.
    if data_id == 7:
        reversed_bytes = chunk[::-1]
        interval = int.from_bytes(reversed_bytes[0:2], byteorder="big", signed=False)
        power = int.from_bytes(reversed_bytes[2:4], byteorder="big", signed=False)
        return {"interval_min": interval, "battery_pct": power}

    # AI model info: 3 single-byte fields in the high-order bytes.
    if data_id == 9:
        reversed_bytes = chunk[::-1]
        return {
            "detection_type": reversed_bytes[0],
            "model_id": reversed_bytes[1],
            "model_ver": reversed_bytes[2],
        }

    # 0x120 (remove sensor) and any other special id with no payload meaning.
    return None


def parse_sensecap_s210x(hex_str: str, port: int) -> dict:
    """
    Decode SenseCAP S210X hex string payload from LoRaWAN network.
    Return a flat dict containing sensor measurements and selected metadata.

    The wire format consists of 7-byte frames followed by a 2-byte CRC trailer.
    CRC is not validated here; the network server is assumed to have done so.
    Unknown data_ids are silently ignored.

    The ``port`` argument is accepted for API consistency with other parsers
    in this package but is not used for decoding (SenseCAP S210X is not bound
    to a specific LoRaWAN FPort).
    """
    data: dict[str, Any] = {}
    try:
        raw = bytes.fromhex("".join(hex_str.split()))
    except ValueError:
        return data
    if len(raw) < 2:
        return data
    body = raw[:-2]
    if len(body) == 0 or len(body) % 7 != 0:
        return data

    eui_low: Optional[str] = None
    eui_high: Optional[str] = None

    for i in range(0, len(body), 7):
        frame = body[i : i + 7]
        # Frame layout: channel(1) | data_id(2, LE) | value(4)
        data_id = int.from_bytes(frame[1:3], byteorder="little", signed=False)
        value_bytes = frame[3:7]

        if data_id > 4096:
            name = _MEASUREMENT_NAMES.get(data_id, f"data_id_{data_id}")
            data[name] = _decode_signed_le_4bytes(value_bytes)
            continue

        if data_id in _SPECIAL_IDS:
            decoded = _decode_special(data_id, value_bytes)
            if data_id == 0:
                # "1.2,3.4" -> hardware, software
                hw, _, sw = (decoded or "").partition(",")
                data["hardware_version"] = hw
                data["software_version"] = sw
            elif data_id == 1:
                data["sensor_version"] = decoded
            elif data_id == 2:
                eui_low = decoded
            elif data_id == 3:
                eui_high = decoded
            elif data_id == 4:
                data["timestamp_field"] = decoded
            elif data_id == 7:
                data["battery_pct"] = decoded["battery_pct"]
                data["interval_sec"] = decoded["interval_min"] * 60
            elif data_id == 9:
                data["detection_type"] = decoded["detection_type"]
                data["model_id"] = decoded["model_id"]
                data["model_ver"] = decoded["model_ver"]
            elif data_id == 0x120:
                data["remove_sensor"] = True

    if eui_high and eui_low:
        data["sensor_eui"] = (eui_high + eui_low).upper()

    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    return parse_sensecap_s210x(hex_str, port)


def create_datalines(hex_str: str, port: int, time_str: Optional[str] = None) -> list:
    """
    Return well-known parsed data formatted list of data, e.g.
    [
      {
        "time": "2022-03-02T12:21:30.123000+00:00",
        "data": {
          "air_temperature": 25.5,
          "air_humidity": 60.2
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
        # air_temperature 25.5, air_humidity 60.2
        ("0101109c63000001021028eb0000d68f", 1),
        # soil_temperature_vwc_ec 21.5, soil_volumetric_water_content 35.25, soil_electrical_conductivity 1.234
        ("011010fc530000010e10b2890000010f10d20400000536", 1),
        # battery_pct 85, interval_sec 3600 (60 min)
        ("01070055003c004727", 1),
        # Real example data
        ("01061054560000010710E80300004076", 2),
        ("010610F0550000010710840300003D22", 2),
        ("0106101C570000010710840300001825", 2),
    ]
    main(examples)
