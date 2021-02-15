# https://github.com/decentlab/decentlab-decoders/blob/master/DL-MBX/DL-MBX.py
# https://www.decentlab.com/products/ultrasonic-distance-/-level-sensor-for-lorawan


import struct
import binascii

PROTOCOL_VERSION = 2

# Do not change the names below
SENSORS = [
    {
        "length": 2,
        "values": [
            {"name": "distance", "convert": lambda x: x[0]},
            {"name": "valid_samples", "convert": lambda x: x[1]},
        ],
    },
    {
        "length": 1,
        "values": [
            {"name": "batt", "convert": lambda x: x[0] / 1000}
        ]
    },
]


def parse_dlmbx(hex_str: str, port: int = None):
    """hex_str: payload as hex string"""
    bytes_ = bytearray(binascii.a2b_hex(hex_str))
    version = bytes_[0]
    if version != PROTOCOL_VERSION:
        raise ValueError("protocol version {} doesn't match v2".format(version))

    devid = struct.unpack(">H", bytes_[1:3])[0]
    bin_flags = bin(struct.unpack(">H", bytes_[3:5])[0])
    flags = bin_flags[2:].zfill(struct.calcsize(">H") * 8)[::-1]
    words = [struct.unpack(">H", bytes_[i: i + 2])[0] for i in range(5, len(bytes_), 2)]

    cur = 0
    result = {
        "dl_id": devid,  # Decent lab device id
        "protocol": version
    }
    for flag, sensor in zip(flags, SENSORS):
        if flag != "1":
            continue

        x = words[cur: cur + sensor["length"]]
        cur += sensor["length"]
        for value in sensor["values"]:
            if "convert" not in value:
                continue
            result[value["name"]] = value["convert"](x)

    return result


def decode_hex(hex_str: str, port: int = None):
    return parse_dlmbx(hex_str, port=port)


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        payloads = [sys.argv[1]]
    else:
        payloads = [
            "02012f000304d200010bb1",
            "02012f00020bb1",
            "0218d7000309d5000f0ac4",
        ]
    for pl in payloads:
        print(json.dumps(decode_hex(pl), indent=2))
