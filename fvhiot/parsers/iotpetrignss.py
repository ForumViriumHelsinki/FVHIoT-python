"""
# Parser for Sensoripaja's (IoTPetri's) GNSS tracker data format.

//ESP32 BATTERY VOLTAGE (reform: mydata[0]*8+2500 = # mV)
mydata[0] = (uint16_t)ESPBatteryVoltageScaled;

//COUNTER FOR ATTEMPTS TO GET GNSS SIGNAL
mydata[1] = (uint16_t)findCounter;

//SATELLITES
mydata[2] = (uint16_t)starUserd;

//ALT HIGH (reform: mydata[3-4]/100 = #,# m)
mydata[3] = (uint16_t)altitudeInt >> 8;
mydata[4] = (uint16_t)altitudeInt;

//Lat (reform: mydata[5] = asteet, mydata[6-9] = minuutit ja desimaalit)
mydata[5] = (uint32_t)latPreInt;
mydata[6] = (uint32_t)latInt >> 24;
mydata[7] = (uint32_t)latInt >> 16;
mydata[8] = (uint32_t)latInt >> 8;
mydata[9] = (uint32_t)latInt;

//Lon (reform: mydata[10] = asteet, mydata[11-14] = minuutit ja desimaalit)
mydata[10] = (uint32_t)lonPreInt;
mydata[11] = (uint32_t)lonInt >> 24;
mydata[12] = (uint32_t)lonInt >> 16;
mydata[13] = (uint32_t)lonInt >> 8;
mydata[14] = (uint32_t)lonInt;

//Epoch (reform: mydata[15-19] = unix time)
mydata[15] = (uint32_t)epochInt >> 32;
mydata[16] = (uint32_t)epochInt >> 24;
mydata[17] = (uint32_t)epochInt >> 16;
mydata[18] = (uint32_t)epochInt >> 8;
mydata[19] = (uint32_t)epochInt;

//SOG (reform: mydata[20-21]/100 = #,# knot)
mydata[20] = (uint16_t)sogInt >> 8;
mydata[21] = (uint16_t)sogInt;

//P/H/VDOP
mydata[22] = (uint16_t)pdopInt;
mydata[23] = (uint16_t)hdopInt;
mydata[24] = (uint16_t)vdopInt;

//FIX Status '1'=No fix '2'=2D fix '3'=3D fix
mydata[25] = (uint16_t)fixStatus;

Example payload:
d804090e063c0004711718000e58df0067d7f16d00001e0f1a03

Format:
- Byte 0: Battery voltage (reform: value*8+2500 = mV)
- Bytes 1: GNSS signal attempt counter
- Bytes 2: Satellites used
- Bytes 3-4: Altitude (reform: value/100 = meters)
- Byte 5: Latitude degrees
- Bytes 6-9: Latitude minutes and decimals
- Byte 10: Longitude degrees
- Bytes 11-14: Longitude minutes and decimals
- Bytes 15-19: Unix epoch time
- Bytes 20-21: Speed over ground (reform: value/100 = knots)
- Byte 22: PDOP
- Byte 23: HDOP
- Byte 24: VDOP
- Byte 25: Fix status (1=No fix, 2=2D fix, 3=3D fix)
"""

import datetime
from typing import Optional
from zoneinfo import ZoneInfo


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


def parse_gnss(hex_str: str, port: int) -> dict:
    """
    Decode IoTPetri's GNSS tracker hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    data = {}

    # Battery voltage
    batt_raw = int(hex_str[0:2], 16)
    data["batt"] = batt_raw * 8 + 2500

    # GNSS signal attempts and satellites
    data["gnss_attempts"] = int(hex_str[2:4], 16)
    data["satellites"] = int(hex_str[4:6], 16)

    # Altitude
    alt_raw = int(hex_str[6:10], 16)
    data["altitude"] = alt_raw / 100

    # Latitude
    lat_deg = int(hex_str[10:12], 16)
    lat_min = int(hex_str[12:20], 16)
    data["latitude"] = lat_deg + (lat_min / 1000000)

    # Longitude
    lon_deg = int(hex_str[20:22], 16)
    lon_min = int(hex_str[22:30], 16)
    data["longitude"] = lon_deg + (lon_min / 1000000)

    # Unix timestamp
    data["timestamp"] = int(hex_str[30:40], 16)

    # Speed over ground
    sog_raw = int(hex_str[40:44], 16)
    data["speed"] = sog_raw / 100

    # DOP values
    data["pdop"] = int(hex_str[44:46], 16) / 10
    data["hdop"] = int(hex_str[46:48], 16) / 10
    data["vdop"] = int(hex_str[48:50], 16) / 10

    # Fix status
    data["fix_status"] = int(hex_str[50:52], 16)

    return data


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    """
    return parse_gnss(hex_str, port)


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
        ["d904060ed83c0003659e18000d59b70067d6f62a00004d393303", 1],  # example data
        ["d804090e4c3c0003662618000d59090067d7f2b700001d0f1903", 1],  # example data
        ["d1040709243c0003663e18000d593d0067d761b0000021121c03", 1],  # example data
        ["d804090dac3c0003661518000d58fb0067d7f54b00001c0e1803", 1],  # example data
        ["ce040d0cda3c0003665418000d59380067d7d3a90000130a1003", 1],  # example data
        ["cd040d096a3c0003665b18000d59200067d7ae100000140c1003", 1],  # example data
        ["d7040a0aaa3c0003664918000d58f30067d7099e0000120c0e03", 1],  # example data
        ["d804090e063c0003661718000d58df0067d7f16d00001e0f1a03", 1],  # example data
    ]
    main(examples)
