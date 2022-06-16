import argparse
import datetime
import logging
import os
import time
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

from influxdb import InfluxDBClient as InfluxDBClient_v1


def get_influxdb_args_v1(env: bool = False) -> Tuple[str, str, str, str, str, bool, bool]:
    """
    Parse InfluxDB connection parameters from command line arguments or get them from envs.

    :param env: True, if arguments should be taken from envs.
    :return: host, port, database, user, password
    """
    if env:
        host, port, database, username, password, ssl, verify_ssl = (
            os.getenv("INFLUXDB_HOST"),
            os.getenv("INFLUXDB_PORT"),
            os.getenv("INFLUXDB_DATABASE"),
            os.getenv("INFLUXDB_USERNAME"),
            os.getenv("INFLUXDB_PASSWORD"),
            True if os.getenv("INFLUXDB_SSL") is not None else False,
            True if os.getenv("INFLUXDB_VERIFY_SSL") is not None else False,
        )
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", help="InfluxDB host", required=True)
        parser.add_argument("--port", help="InxluxDB port", default="8086", required=False)
        parser.add_argument("--database", help="InfluxDB database", required=True)
        parser.add_argument("--username", help="InfluxDB username", required=False)
        parser.add_argument("--password", help="InfluxDB password", required=False)
        parser.add_argument("--ssl", help="Use SSL", action="store_true")
        parser.add_argument("--verify_ssl", help="Verify SSL certificate", action="store_true")
        args = parser.parse_args()
        host, port, database, username, password = args.host, args.port, args.database, args.username, args.password
        ssl, verify_ssl = args.ssl, args.verify_ssl
    pw = "None" if password is None else "*****"
    logging.info(
        f"Got InfluxDB parameters host={host}, port={port}, database={database}, username={username}, password={pw}"
    )
    return host, port, database, username, password, ssl, verify_ssl


def create_influxdb_client_v1(
    host: str, port: str, database: str, username: str, password: str, ssl: bool, verify_ssl: bool
) -> InfluxDBClient_v1:
    """
    Initialize InfluxDBClient using host, database and optionally username and password.
    """
    return InfluxDBClient_v1(
        host=host, port=port, database=database, username=username, password=password, ssl=ssl, verify_ssl=verify_ssl
    )


def create_influxdb_dict(
    dev_id: str, measurement_name: str, fields: dict, tags: Optional[dict], timestamp: Optional[datetime.datetime]
) -> dict:
    """
    Convert arguments to a valid InfluxDB measurement dict.

    :param dev_id: device id, mandatory tag for InfluxDB
    :param measurement_name:
    :param fields: dict containing metrics
    :param tags: dict containing additional tags
    :param timestamp: timezone aware datetime
    :return: valid InfluxDB line protocol string
    """
    if timestamp is None:
        timestamp = datetime.datetime.now(ZoneInfo("UTC"))
    else:
        # Make sure datetime is timezone aware and in UTC time
        timestamp = timestamp.astimezone(ZoneInfo("UTC"))
    if tags is None:
        tags = {}
    # For historical reasons the main identifier (tag) is "dev-id"
    tags.update({"dev-id": dev_id})
    return {"measurement": measurement_name, "tags": tags, "fields": fields, "time": "{}".format(timestamp.isoformat())}


# The query that connects to influxDB
def test_query_v1(client: InfluxDBClient_v1):
    """
    Test connection to InfluxDB 1.x Database.
    Print measurements if connection was successful
    """
    query = "show measurements"
    result = client.query(query)
    for measurements in result:
        for measure in measurements:
            print(measure)


# This function is called from the main.py module. [url, token, org] are in separate module called credits.py
def main():
    host, port, database, username, password, ssl, verify_ssl = get_influxdb_args_v1()
    c = create_influxdb_client_v1(host, port, database, username, password, ssl, verify_ssl)
    test_query_v1(c)


if __name__ == "__main__":
    main()
