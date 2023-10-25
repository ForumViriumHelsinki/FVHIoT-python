import datetime
import struct
from typing import Optional
from zoneinfo import ZoneInfo
from ..utils.lorawan.thingpark import get_uplink_obj


def hex2int(hex_str: str) -> int:
    """
    Convert hex characters (e.g. "23" or "011a") to int (35 or 282)

    :param hex_str: hex character string
    :return: int integer
    """
    return int(hex_str, 16)


def hex2value10(hex_str: str) -> float:
    """
    Convert 2 hex characters (e.g. "23") to float (3.5)

    :param hex_str: hex character string
    :return: float value
    """
    return hex2int(hex_str) / 10.0


def parse_ircounter(hex_str, port: int):
    """
    Parse payload like "d77e3700030002" or "d77e070dae3700040001" struct of mixed values

    :param hex_str: IR counter hex payload
    :param port: LoRaWAN port
    :return: dict containing values
    """
    data = None

    if hex_str[4:6] == "07":
        data = {
            "voltage": int(hex_str[6:10], 16),  # millivolts in pcb not at car battery
            "in": int(hex_str[12:16]),
            "out": int(hex_str[16:20]),
        }

    if hex_str[4:6] == "37":
        data = {
            "in": int(hex_str[6:10]),
            "out": int(hex_str[10:14]),
        }

    return data


def parse_victron(hex_str, port: int):
    """
    Parse payload like
    "0a00000000e83c4600a83b4600000000000000000000ba42000000000000000000008041000081430000000000000000"
    struct of mixed values

    :param hex_str: Victron hex payload
    :param port: LoRaWAN port
    :return: dict containing values
    """

    b = bytes.fromhex(hex_str)
    val = struct.unpack("<Bbxxfffffffffii", b)

    data = {
        # 2  float mainVoltage_V;      // mV
        # 3  float panelVoltage_VPV;   // mV
        # 4  float panelPower_PPV;     // W
        # 5  float batteryCurrent_I;   // mA
        # 6  float yieldTotal_H19;     // 0.01 kWh
        # 7  float yieldToday_H20;     // 0.01 kWh
        # 8  float maxPowerToday_H21;  // W
        # 9  float yieldYesterday_H22; // 0.01 kWh
        # 10  float maxPowerYesterday_H23; // W
        # 11  int errorCode_ERR;
        # 12  int stateOfOperation_CS;
        "mainvoltage": val[2],
        "panelvoltage": val[3],
        "panelpower": val[4],
        "batterycurrent": val[5],
        "errorcode": val[11],  # int
        "state": val[12],  # int
    }
    return data


def parse_victronphoenix(hex_str, port: int):
    """
    Parse payload like "0a0200000000000000000000000000000000000000004765d8590000fa0000090000" struct of mixed values

    :param hex_str: Victron hex payload
    :param port: LoRaWAN port
    :return: dict containing values
    :c uint8 = B
    :c uint16 = H x = filling
    """

    b = bytes.fromhex(hex_str)
    val = struct.unpack("<BbHHHhHHHHHBBHHHBBBBBx", b)

    data = {
        # 0  msgtype
        # 1  msg_ver
        # MPPT
        # 2  uint16 mainVoltage_V;      // mV
        # 3  uint16 panelVoltage_VPV;   // mV ( value needs to be divided by 10 )
        # 4  uint16 panelPower_PPV;     // W
        # 5  int6 batteryCurrent_I;   // mA ( value needs to be divided by 10 )
        # 6  uint16 yieldTotal_H19;     // 0.01 kWh
        # 7  uint16 yieldToday_H20;     // 0.01 kWh
        # 8  uint16 maxPowerToday_H21;  // W
        # 9  uint16 yieldYesterday_H22; // 0.01 kWh
        # 10  uint16 maxPowerYesterday_H23; // W
        # 11  uint8 errorCode_ERR;
        # 12  uint8 stateOfOperation_CS;
        # Phoenix
        # 13 uint16_t p_V;      // mV
        # 14 uint16_t p_AC_OUT_V;
        # 15 uint16_t p_AC_OUT_S;
        # 16 uint8_t p_AC_OUT_I;
        # 17 uint8_t p_WARN; // Same as ar but for now can be multiple bits
        # 18 uint8_t p_AR; // alarm convert to 8 bit
        # 19 uint8_t p_CS; // convert to 8 bit
        # 20 uint8_t p_MODE;
        "mpptmainvoltage": val[2],
        "mpptpanelvoltage": val[3] / 10,
        "mpptpanelpower": val[4],
        "mpptbatterycurrent": val[5] / 10,
        "mpptyieldTotal": val[6],
        "mpptyieldToday": val[7],
        "mpptmaxPowerToday": val[8],
        "mpptyieldYesterday": val[9],
        "mpptmaxPowerYesterday": val[10],
        "mppterrorcode": val[11],  # int
        "mpptstate": val[12],  # int
        "p_V": val[13],
        "p_AC_OUT_V": val[14],
        "p_AC_OUT_S": val[15],
        "p_AC_OUT_I": val[16],
        "p_WARN": val[17],
        "p_AR": val[18],
        "p_CS": val[19],
        "p_MODE": val[20],
    }
    return data


def parse_davisweather(hex_str, port: int):
    """
    Parse payload like "0700fd729601575293010b12fe00000000ffff7f580013b40000aa000002590300c1" struct of mixed values

    :param hex_str: Davis weather station hex payload
    :param port: LoRaWAN port
    :return: dict containing values
    """

    b = bytes.fromhex(hex_str)
    val = struct.unpack("<BbHhBxhBBHBHBHHHHHHBHB", b)  # Capital is unsigned, b 8bit h 16bit, x 8bit padding
    data = {
        # 0  int DavisDataCode 07
        # 1  data version 0
        # 2  uint16_t Current barometer as (Hg / 1000)
        # 3  int16_t Inside Temperature as (DegF / 10)
        # 4  uint8_t Inside Humidity as percentage
        # 5  int16_t Outside Temperature as (DegF / 10)
        # 6  uint8_t Wind Speed
        # 7  uint8_t 10-Minute Average Wind Speed
        # 8  uint16_t Wind Direction in degress
        # 9  uint8_t Outside Humidity
        # 10 uint16_t Rain Rate
        # 11 uint8_t UV Level
        # 12 uint16_t Solar Radiation
        # 13 uint16_t Total Storm Rain
        # 14 uint16_t Start date of current storm
        # 15 uint16_t Rain Today
        # 16 uint16_t Rain this Month
        # 17 uint16_t Rain this Year
        # 18 uint8_t Transmitter battery status
        # 19 uint16_t Console Battery Level:
        # 20 uint8_t Forecast Icon
        # 21 uint8_t Forecast rule number
        "barometer": round(((val[2] / 1000) * 33.86389), 1),
        "in_temperature": round((((val[3] / 10) - 32) / 1.8), 1),
        "in_humity": val[4],
        "out_temperature": round((((val[5] / 10) - 32) / 1.8), 1),
        "windspeed": val[6],
        "10minwind": val[7],
        "winddirection": val[8],
        "out_humity": val[9],
        "rain": val[10],
        "raintoday": val[15],
    }
    return data


def parse_aurinkopenkki(hex_str, port: int):
    """
    Parse payload like "3a2c0000018906438046933f478a773cc82a00003501000000000000113b00002f000000" float values

    :param hex_str: EnergiaBurk hex payload
    :param port: LoRaWAN port
    :return: dict containing float values
    """
    b = bytes.fromhex(hex_str)
    val = struct.unpack("<BbxxfffIIIII", b)

    # struct t_AcudcDATA {
    # uint8_t msg_type;
    # uint8_t msg_ver;
    # float volt;
    # float amp;
    # float watt;
    # uint32_t runTime;
    # uint32_t inEnergy;
    # uint32_t outEnergy;
    # uint32_t inAh;
    # uint32_t outAh;

    data = {
        "voltage": val[2],
        "current": val[3],
        "power": val[4],
        "runtime": val[5],
        "inEnergy": val[6],
        "outEnergy": val[7],
        "inmAh": val[8],
        "outmAh": val[9],
    }
    return data


def parse_voltageburk(hex_str, port: int):
    """
    Parse payload like "3a2c007d0003002a000000000000000000000000" float values

    :param hex_str: EnergiaBurk hex payload
    :param port: LoRaWAN port
    :return: dict containing float values
    """
    b1 = bytes.fromhex(hex_str[-8:])
    volt = struct.unpack("<f", b1)[0]
    data = {
        "voltage": volt,
    }
    return data


def parse_energiaburk(hex_str: str, port: int):
    """
    Parse payload like "3a2c007d0003002a000000000000000000000000" float values

    :param hex_str: EnergiaBurk hex payload
    :param port: LoRaWAN port
    :return: dict containing float values
    """
    if hex_str.startswith("3a"):
        return parse_aurinkopenkki(hex_str, port)
    elif hex_str.startswith("09"):
        return parse_voltageburk(hex_str, port)
    elif hex_str.startswith("0a00"):
        return parse_victron(hex_str, port)
    elif hex_str.startswith("0a02"):
        return parse_victronphoenix(hex_str, port)
    elif hex_str.startswith("0700"):
        return parse_davisweather(hex_str, port)
    elif hex_str.startswith("d77e"):
        return parse_ircounter(hex_str, port)


def decode_hex(hex_str: str, port: int) -> dict:
    """
    Decode hex string payload from LoRaWAN network.
    Return a dict containing sensor data.
    NOTE: this is here for backwards compatibility.
    """
    return parse_energiaburk(hex_str, port)


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
          "voltage": 13.575298309326172,
          "current": -0.8191490173339844,
          "power": -11.269439697265625,
          "runtime": 651510,
          "inEnergy": 1427,
          "outEnergy": 3936,
          "inmAh": 121252,
          "outmAh": 296495
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
        ("d77e3700030002", 1),
        ("d77e070dae3700040001", 1),
        ("0a00000000e83c4600a83b4600000000000000000000ba42000000000000000000008041000081430000000000000000", 1),
        ("0a0200000000000000000000000000000000000000004765d8590000fa0000090000", 1),
        ("0700fd729601575293010b12fe00000000ffff7f580013b40000aa000002590300c1", 1),
        ("3a2c0000018906438046933f478a773cc82a00003501000000000000113b00002f000000", 1),
        ("3a2c007d0003002a000000000000000000000000", 1),
        ("3a2c007d0003002a000000000000000000000000", 1),
        ("3a2c00006c345941c0b351bfa04f34c1f6f0090093050000600f0000a4d901002f860400", 1),
    ]
    main(examples)
