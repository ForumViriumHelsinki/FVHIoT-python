import asyncio
import logging
import os

from typing import List

import certifi

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, TopicPartition
from aiokafka.errors import NoBrokersAvailable
from aiokafka.helpers import create_ssl_context
from aiokafka.structs import RecordMetadata


def on_send_success(record_metadata: RecordMetadata):
    """Log send success"""
    logging.info(
        "Successfully sent to topic {}, partition {}, offset {}".format(
            record_metadata.topic, record_metadata.partition, record_metadata.offset
        )
    )


def on_send_error(excp):
    """Log send error"""
    logging.error("Error on Kafka producer", exc_info=excp)


async def get_aiokafka_producer(
    bootstrap_servers: List[str] = None,
    security_protocol: str = None,
    ssl_cafile: str = None,
    ssl_certfile: str = None,
    ssl_keyfile: str = None,
    sasl_mechanism: str = None,
    sasl_plain_username: str = None,
    sasl_plain_password: str = None,
) -> AIOKafkaProducer:
    """
    Simply create and return a KafkaProducer using given arguments.
    """
    ssl_cafile = ssl_cafile or certifi.where()
    ssl_context = create_ssl_context(cafile=ssl_cafile, certfile=ssl_certfile, keyfile=ssl_keyfile)
    kp = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,
        ssl_context=ssl_context,
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password,
    )
    await kp.start()
    return kp


async def get_aiokafka_producer_by_envs():
    """
    Create and return Kafkaproducer, which is initialized by values from environment variables.
    At least these variables must usually be defined to make the connection to brokers:
    KAFKA_SASL_USERNAME
    KAFKA_SASL_PASSWORD
    KAFKA_BOOTSTRAP_SERVERS
    KAFKA_SECURITY_PROTOCOL
    KAFKA_SASL_MECHANISMS
    """
    logging.info("Getting KafkaProducer: {}".format(os.getenv("KAFKA_BOOTSTRAP_SERVERS")))
    try:
        kp = await get_aiokafka_producer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "").split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_SSL_CA_LOCATION"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
            sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISMS"),
            sasl_plain_username=os.getenv("KAFKA_SASL_USERNAME"),
            sasl_plain_password=os.getenv("KAFKA_SASL_PASSWORD"),
        )
        return kp
    except NoBrokersAvailable as err:
        logging.error(f"Failed to get KafkaProducer: {err}")
        return None


async def get_aiokafka_consumer(
    topics: List[str],
    bootstrap_servers: List[str] = None,
    security_protocol: str = None,
    ssl_cafile: str = None,
    ssl_certfile: str = None,
    ssl_keyfile: str = None,
    sasl_mechanism: str = None,
    sasl_plain_username: str = None,
    sasl_plain_password: str = None,
    group_id: str = None,
    auto_offset_reset="latest",
    enable_auto_commit: bool = False,
    offset: int = 0,
):
    """
    Simply create and return a KafkaConsumer using given arguments.
    Use seek_to_offset() to subscribe to given topic(s) and seek to default offset 0.

    Note: the consumer is already started here, thus it suffices to simply start
          consuming messages in the main app.
    """
    ssl_cafile = ssl_cafile or certifi.where()
    ssl_context = create_ssl_context(cafile=ssl_cafile, certfile=ssl_certfile, keyfile=ssl_keyfile)
    kc = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,
        ssl_context=ssl_context,
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=enable_auto_commit,
    )
    logging.info("Starting KafkaConsumer and subscribing to topics: {}".format(topics))
    await kc.start()
    for topic in topics:
        await seek_to_offset(kc, topic, offset)
    return kc


async def get_aiokafka_consumer_by_envs(
    topics: List[str], auto_offset_reset: str = "latest", enable_auto_commit: bool = False, offset: int = 0
):
    """
    Create and return KafkaConsumer, which is initialized by values from environment variables.
    At least these variables must usually be defined to make the connection to brokers:
    KAFKA_SASL_USERNAME
    KAFKA_SASL_PASSWORD
    KAFKA_BOOTSTRAP_SERVERS
    KAFKA_SECURITY_PROTOCOL
    KAFKA_SASL_MECHANISMS
    """
    logging.info("Getting KafkaConsumer: {}".format(os.getenv("KAFKA_BOOTSTRAP_SERVERS")))
    try:
        kc = await get_aiokafka_consumer(
            topics,
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "").split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_SSL_CA_LOCATION"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
            sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISMS"),
            sasl_plain_username=os.getenv("KAFKA_SASL_USERNAME"),
            sasl_plain_password=os.getenv("KAFKA_SASL_PASSWORD"),
            group_id=os.getenv("KAFKA_GROUP_ID"),
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit,
            offset=offset,
        )
        return kc
    except NoBrokersAvailable as err:
        logging.error(f"Failed to get KafkaConsumer: {err}")
        return None


async def seek_to_offset(consumer: AIOKafkaConsumer, topic: str, start: int = -1):
    """
    Seek to the last message in topic.
    """
    partition_number, offset = -1, -1
    # Loop through partitions and find the latest offset
    for p in consumer.partitions_for_topic(topic):
        tp = TopicPartition(topic, p)
        committed = await consumer.committed(tp)
        await consumer.seek_to_end(tp)
        last_offset = await consumer.position(tp)
        # print("topic: {} partition: {} committed: {} last: {}".format(topic, p, committed, last_offset))
        if offset < last_offset:
            offset = last_offset
            partition_number = p
    tp = TopicPartition(topic, partition_number)
    consumer.seek(tp, offset - start)
