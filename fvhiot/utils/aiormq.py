import logging
import os
import re
import socket
from typing import Optional

import aiorabbit
import aiorabbit.exceptions
from aiorabbit.client import Client


async def create_headers_exchange(client: Client, exchange_name: str):
    """Create headers exchange and log it"""
    logging.info(f"Creating headers exchange: {exchange_name} ")
    await client.exchange_declare(
        exchange=exchange_name,
        exchange_type="headers",
        durable=True,
        auto_delete=False,
    )


async def get_aiorabbitmq_client(url: str) -> Client:
    """
    Simply create and return an aiorabbit.client.Client using given
    connection url and log it. Raise error if connection fails.
    """
    logging.info("Connecting to RabbitMQ using url: {}".format(re.sub(":.*@", ":*****@", url)))
    client = Client(url)
    try:
        await client.connect()
        await client.confirm_select()
        return client
    except (aiorabbit.exceptions.AccessRefused, socket.gaierror) as err:
        logging.error(f"Failed to connect to RabbitMQ: {err}")
        raise


async def get_aiorabbitmq_client_by_envs() -> Optional[Client]:
    """
    Return an aiorabbit.client.Client, if RABBITMQ_URL exists and
    connection is successful, otherwise return None
    """
    url = os.getenv("RABBITMQ_URL")
    if url is None:
        return None
    client = await get_aiorabbitmq_client(url)
    return client
