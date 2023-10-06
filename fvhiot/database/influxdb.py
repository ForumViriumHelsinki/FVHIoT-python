import argparse
import collections
import datetime
import logging
import os
import time
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


def get_influxdb_args() -> Tuple[str, str, str, str]:
    """
    Parse InfluxDB connection parameters from command line arguments or get them from envs.

    :param env: True, if get arguments from envs.
    :return: host, token, org, bucket
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--influx-host", help="InfluxDB host", default=os.getenv("INFLUX_HOST"), required=False)
    parser.add_argument("--influx-org", help="InfluxDB organization", default=os.getenv("INFLUX_ORG"), required=False)
    parser.add_argument("--influx-token", help="InfluxDB token", default=os.getenv("INFLUX_TOKEN"), required=False)
    parser.add_argument(
        "--influx-bucket", help="InfluxDB bucket name", default=os.getenv("INFLUX_BUCKET"), required=False
    )
    # Deprecated args: --->
    parser.add_argument("--influxdb-url", help="Deprecated", default=os.getenv("INFLUXDB_URL"), required=False)
    parser.add_argument("--influxdb-token", help="InxluxDB token", default=os.getenv("INFLUXDB_TOKEN"), required=False)
    parser.add_argument(
        "--influxdb-org", help="InfluxDB organization", default=os.getenv("INFLUXDB_ORG"), required=False
    )
    parser.add_argument(
        "--influxdb-bucket", help="InfluxDB bucket name", default=os.getenv("INFLUXDB_BUCKET"), required=False
    )
    # <--- Deprecated args end
    args, unknown = parser.parse_known_args()
    args_dict = vars(args)
    # Check that mandatory variables are present
    missing_arg = influx2_arg = None
    for arg in ["INFLUX_HOST", "INFLUX_TOKEN", "INFLUX_ORG", "INFLUX_BUCKET"]:
        if args_dict[arg.lower()] is None:
            # TODO: replace missing_arg with RuntimeError
            missing_arg = arg
            influx2_arg = arg
            # raise RuntimeError(
            #     "Parameter missing: add --{} or {} environment variable".format(arg.lower().replace("_", "-"), arg)
            # )
            break

    if missing_arg is None:
        host, token, org, bucket = args.influx_host, args.influx_token, args.influx_org, args.influx_bucket
    else:
        for arg in ["INFLUXDB_URL", "INFLUXDB_TOKEN", "INFLUXDB_ORG", "INFLUXDB_BUCKET"]:
            if args_dict[arg.lower()] is None:
                missing_arg = arg
        host, token, org, bucket = args.influxdb_url, args.influxdb_token, args.influxdb_org, args.influxdb_bucket
    if missing_arg:
        raise RuntimeError(
            "Parameter missing: add --{} or {} environment variable".format(influx2_arg.lower().replace("_", "-"), influx2_arg)
        )
    logging.info(f"Got InfluxDB parameters host={host}, token=*****, org={org}, bucket={bucket}")
    return host, token, org, bucket


def create_influxdb_client(url: str, token: str, org: str) -> InfluxDBClient:
    """
    Initialize InfluxDBClient using authentication token and InfluxDB url.

    :return: InfluxDBClient
    """
    # You can generate a Token from the "Tokens Tab" in the UI
    return InfluxDBClient(url=url, token=token, org=org)


def create_influxdb_line(
    dev_id: str, measurement_name: str, fields: dict, tags: Optional[dict], timestamp: Optional[datetime.datetime]
) -> str:
    """
    Convert arguments to a valid InfluxDB line protocol string.

    :param dev_id: device id, mandatory tag for InfluxDB
    :param measurement_name:
    :param fields: dict containing metrics
    :param timestamp: timezone aware datetime
    :param tags: dict containing additional tags
    :return: valid InfluxDB line protocol string
    """
    if timestamp is None:
        time_int = int(time.time() * 10**9)
    else:
        # Make sure datetime is timezone aware and in UTC time
        timestamp = timestamp.astimezone(ZoneInfo("UTC"))
        time_int = int(timestamp.timestamp() * 10**9)  # epoch in nanoseconds
    if tags is None:
        tags = {}
    # For historical reasons the main identifier (tag) is "dev-id"
    tags.update({"dev-id": dev_id})
    # Convert dict to sorted comma separated list of key=val pairs, e.g. tagA=foo,tagB=bar
    tag_str = ",".join([f"{i[0]}={i[1]}" for i in sorted(list(tags.items()))])
    for k, v in fields.items():
        fields[k] = float(v)
    field_str = ",".join([f"{i[0]}={i[1]}" for i in sorted(list(fields.items()))])
    # measurement,tag1=val1 field1=3.8234,field2=4.23874 1610089552385868032
    measurement = f"{measurement_name},{tag_str} {field_str} {time_int}"
    return measurement


def create_influxdb_dict(
    dev_id: str,
    measurement_name: str,
    fields: dict,
    tags: Optional[dict],
    timestamp: Optional[datetime.datetime],
    convert_floats: bool = False,
) -> dict:
    """
    Convert arguments to a valid InfluxDB measurement dict.

    :param dev_id: device id, mandatory tag for InfluxDB
    :param measurement_name:
    :param fields: dict containing metrics
    :param tags: dict containing additional tags
    :param timestamp: timezone aware datetime
    :param convert_floats: True if all values should be converted to floats
    :return: valid InfluxDB dict object
    """
    if timestamp is None:
        timestamp = datetime.datetime.now(ZoneInfo("UTC"))
    else:
        # Make sure datetime is timezone aware and in UTC time
        timestamp = timestamp.astimezone(ZoneInfo("UTC"))
    if tags is None:
        tags = {}
    if convert_floats:
        for k, v in fields.items():  # Convert all fields to floats
            fields[k] = float(v)
    # For historical reasons the main identifier (tag) is "dev-id"
    tags.update({"dev-id": dev_id})
    return {"measurement": measurement_name, "tags": tags, "fields": fields, "time": "{}".format(timestamp.isoformat())}


def write_data(client: InfluxDBClient, bucket: str, org: str, data_obj: dict):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket, org, data_obj)
    write_api.close()


# The query that connects to influxDB
def test_query(client):
    query_api = client.query_api()
    q = """
    from(bucket: "AapoTest")
      |> range(start: 2021-05-01T00:00:00Z, stop: 2021-05-02T00:00:00Z)
      |> filter(fn: (r) => r["_measurement"] == "aq")
      |> filter(fn: (r) => r["_field"] == "pm10" or r["_field"] == "pm25")
      |> filter(fn: (r) => r["dev-id"] == "84:0D:8E:8F:51:6E")
      |> yield(name: "mean")
    """
    result = query_api.query(query=q)
    results = []
    for table in result:
        for record in table.records:
            d = collections.OrderedDict()
            d[record.get_field()] = record.get_value()
            results.append(d)
    print("Query done")
    return results


# This function is called from the main.py module. [url, token, org] are in separate module called credits.py
def main():
    import random

    url, token, org, bucket = get_influxdb_args(env=True)
    d = create_influxdb_dict("1234", "test", {"temp": 42 + random.random()}, {}, None)
    c = create_influxdb_client(url, token, org)
    write_data(c, bucket, org, d)
    # with InfluxDBClient(url=url, token=token, org=org) as client:
    #     results = test_query(client)
    #     return results


if __name__ == "__main__":
    main()
