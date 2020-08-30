def get_value(hex_str: str, data: dict):
    if hex_str[:2] == '01':
        end = 6
        data['temp'] = int(hex_str[2:end], 16) / 10
        hex_str = hex_str[end:]
    if hex_str[:2] == '02':
        end = 4
        data['humi'] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    if hex_str[:2] == '04':
        end = 6
        data['lux'] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    if hex_str[:2] == '05':
        end = 4
        data['motion'] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    if hex_str[:2] == '06':
        end = 6
        data['co2'] = int(hex_str[2:end], 16)
        hex_str = hex_str[end:]
    if hex_str[:2] == '07':
        end = 6
        data['volt'] = int(hex_str[2:end], 16) / 1000
        hex_str = hex_str[end:]
    else:
        data['error'] = hex_str
        hex_str = ''
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


if __name__ == '__main__':
    import sys

    try:
        print(parse_elsys(sys.argv[1], int(sys.argv[2])))
    except IndexError as err:
        print('Some examples:')
        for s in [('010112022d0400f20504060140070e51', 5),
                  ('010109022f0400000500060224070e38', 5),
                  ('010102022f0400000500060275070e4f', 5),
                  ]:
            print(parse_elsys(s[0], s[1]))

        print(f'\nUsage: {sys.argv[0]} hex_payload port\n\n')
