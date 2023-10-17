import json
from datetime import datetime


def create_datalines_from_raw_unpacked_data(unpacked_data: dict) -> list:
    """
        Return well-known parsed data formatted list of data, e.g.
    [
        {
            "time": "2018-02-01T11:22:59.000000",
            "data": {
                "TA120-T246177-N": "45.4",
                "TA120-T246177-O": "false",
                "TA120-T246177-U": "false",
                "TA120-T246177-M": "100",
                "TA120-T246177-S": "044.0,0,0;043.9,0,0;044.2,0,0;044.0,0,0;043.8,0,0;\
                043.9,0,0;044.5,0,0;044.2,0,0;043.8,0,0;044.2,0,0;044.5,0,0;044.7,0,0;\
                044.4,0,0;044.8,0,0;044.2,0,0;045.3,0,0;046.1,0,0;046.5,0,0;046.6,0,0;\
                046.1,0,0;046.3,0,0;046.7,0,0;048.1,0,0;048.5,0,0;048.4,0,0;049.7,0,0;\
                051.6,0,0;047.8,0,0;047.7,0,0;046.7,0,0;046.0,0,0;044.9,0,0;043.9,0,0;\
                043.5,0,0;043.1,0,0;042.5,0,0;043.8,0,0;043.5,0,0;043.4,0,0;043.4,0,0;\
                042.9,0,0;045.2,0,0;043.0,0,0;044.2,0,0;043.4,0,0;044.3,0,0;044.1,0,0;\
                043.2,0,0;043.6,0,0;042.9,0,0;043.1,0,0;043.9,0,0;044.2,0,0;044.1,0,0;\
                048.0,0,0;043.7,0,0;042.9,0,0;048.0,0,0;044.4,0,0;044.5,0,0"
            }
        }
    ]

    """
    json_body = json.loads(unpacked_data["request"]["body"].decode())
    time_string = json_body["sensors"][0]["observations"][0]["timestamp"]
    # Convert the string to a datetime object
    # TODO if different timezone comes up, this needs to be fixed
    time_string = time_string.replace("UTC", "+0000")

    packet_timestamp = datetime.strptime(time_string, "%d/%m/%YT%H:%M:%S%z")
    # Convert the datetime object to a string, to required format
    time_str = packet_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    # get dataline array
    values = json_body["sensors"]
    data = {}
    for item in values:
        data[item["sensor"]] = item["observations"][0]["value"]

    dataline = {"time": time_str, "data": data}
    datalines = [dataline]
    return packet_timestamp, datalines
