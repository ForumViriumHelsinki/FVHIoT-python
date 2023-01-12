import argparse
import logging
import os
from typing import Tuple

from influxdb import InfluxDBClient as InfluxDBClient_v1


def get_influxdb_args_v1() -> Tuple[str, int, str, str, str, bool, bool]:
    """
    Parse InfluxDB connection parameters from command line arguments or get them from envs.

    :param env: True, if arguments should be taken from envs.
    :return: host, port, database, user, password
    """
    ssl = True if os.getenv("INFLUXDB_SSL") is not None else False
    verify_ssl = True if os.getenv("INFLUXDB_VERIFY_SSL") is not None else False
    parser = argparse.ArgumentParser()
    parser.add_argument("--influxdb-host", help="InfluxDB host", default=os.getenv("INFLUXDB_HOST"))
    parser.add_argument(
        "--influxdb-port", help="InxluxDB port", default=int(os.getenv("INFLUXDB_PORT", 8086)), type=int
    )
    parser.add_argument("--influxdb-database", help="InfluxDB database", default=os.getenv("INFLUXDB_DATABASE"))
    parser.add_argument(
        "--influxdb-username", help="InfluxDB username", default=os.getenv("INFLUXDB_USERNAME"), required=False
    )
    parser.add_argument(
        "--influxdb-password", help="InfluxDB password", default=os.getenv("INFLUXDB_PASSWORD"), required=False
    )
    parser.add_argument("--influxdb-ssl", help="Use SSL", default=ssl, action="store_true")
    parser.add_argument("--influxdb-verify-ssl", help="Verify SSL certificate", default=verify_ssl, action="store_true")
    args, unknown = parser.parse_known_args()
    # Check that mandatory variables are present
    args_dict = vars(args)
    for arg in ["INFLUXDB_HOST", "INFLUXDB_PORT", "INFLUXDB_DATABASE"]:
        if args_dict[arg.lower()] is None:
            raise RuntimeError(
                "Parameter missing: add --{} or {} environment variable".format(arg.lower().replace("_", "-"), arg)
            )

    host, port, database, username, password, ssl, verify_ssl = (
        args.influxdb_host,
        args.influxdb_port,
        args.influxdb_database,
        args.influxdb_username,
        args.influxdb_password,
        args.influxdb_ssl,
        args.influxdb_verify_ssl,
    )
    pw = "None" if password is None else "*****"
    logging.info(
        f"Got InfluxDB parameters host={host}, port={port}, database={database}, username={username}, "
        f"password={pw} ssl {ssl}/{verify_ssl}"
    )
    return host, port, database, username, password, ssl, verify_ssl


def create_influxdb_client_v1(
    host: str, port: int, database: str, username: str, password: str, ssl: bool, verify_ssl: bool
) -> InfluxDBClient_v1:
    """
    Initialize InfluxDBClient using host, database and optional username and password.
    """
    return InfluxDBClient_v1(
        host=host, port=port, database=database, username=username, password=password, ssl=ssl, verify_ssl=verify_ssl
    )


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


def main():
    logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=getattr(logging, "DEBUG"))
    host, port, database, username, password, ssl, verify_ssl = get_influxdb_args_v1()
    c = create_influxdb_client_v1(host, port, database, username, password, ssl, verify_ssl)
    test_query_v1(c)


if __name__ == "__main__":
    main()
