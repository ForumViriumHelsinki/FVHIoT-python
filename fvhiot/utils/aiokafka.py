from __future__ import annotations  # Python 3.9 compatibility

import logging
import os

import certifi
from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from kafka.errors import NoBrokersAvailable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
from aiokafka.helpers import create_ssl_context

# New try 03/2022 here:

def get_kafka_producer(
        bootstrap_servers: list[str] = None,
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
    return AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,
        # ssl_check_hostname=self.app.config.get('ssl_check_hostname'],
        ssl_cafile=ssl_cafile or certifi.where(),
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password,
    )


def get_kafka_producer_by_envs():
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
        kc = get_kafka_producer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "").split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_SSL_CA_LOCATION"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
            sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISMS"),
            sasl_plain_username=os.getenv("KAFKA_SASL_USERNAME"),
            sasl_plain_password=os.getenv("KAFKA_SASL_PASSWORD"),
        )
        return kc
    except NoBrokersAvailable as err:
        logging.error(f"Failed to get KafkaProducer: {err}")
        return None


def get_kafka_consumer(
        topic: str | list[str],
        bootstrap_servers: list[str] = None,
        security_protocol: str = None,
        ssl_cafile: str = None,
        ssl_certfile: str = None,
        ssl_keyfile: str = None,
        sasl_mechanism: str = None,
        sasl_plain_username: str = None,
        sasl_plain_password: str = None,
        group_id: str = None,
        enable_auto_commit: bool = False,
        offset: int = 0
):
    """
    Simply create and return a KafkaConsumer using given arguments.
    Use seek_to_offset() to subscribe to given topic(s) and seek to default offset 0
    """
    kc = KafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,
        ssl_cafile=ssl_cafile or certifi.where(),
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password,
        group_id=group_id,
        enable_auto_commit=enable_auto_commit,
    )
    seek_to_offset(kc, topic, offset)
    return kc


def get_kafka_consumer_by_envs(topic: str | list[str], offset: int = 0):
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
        kc = get_kafka_consumer(
            topic,
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "").split(","),
            security_protocol=os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            ssl_cafile=os.getenv("KAFKA_SSL_CA_LOCATION"),
            ssl_certfile=os.getenv("KAFKA_ACCESS_CERT"),
            ssl_keyfile=os.getenv("KAFKA_ACCESS_KEY"),
            sasl_mechanism=os.getenv("KAFKA_SASL_MECHANISMS"),
            sasl_plain_username=os.getenv("KAFKA_SASL_USERNAME"),
            sasl_plain_password=os.getenv("KAFKA_SASL_PASSWORD"),
            group_id=os.getenv("KAFKA_GROUP_ID"),
            enable_auto_commit=False,
            offset=offset,
        )
        return kc
    except NoBrokersAvailable as err:
        logging.error(f"Failed to get KafkaConsumer: {err}")
        return None


def seek_to_offset(consumer: KafkaConsumer, topic: str, start: int = -1):
    """
    Seek to the last message in topic.
    """
    # topic = os.getenv("KAFKA_RAW_DATA_TOPIC_NAME")
    partition_number, offset = -1, -1
    # Loop through partitions and find the latest offset
    for p in consumer.partitions_for_topic(topic):
        tp = TopicPartition(topic, p)
        consumer.assign([tp])
        committed = consumer.committed(tp)
        consumer.seek_to_end(tp)
        last_offset = consumer.position(tp)
        # print("topic: {} partition: {} committed: {} last: {}".format(topic, p, committed, last_offset))
        if offset < last_offset:
            offset = last_offset
            partition_number = p
    tp = TopicPartition(topic, partition_number)
    consumer.seek(tp, offset - start)


# NOTE: arguments are probably about to change


def get_producer(
        bootstrap_servers,
        security_protocol,
        sasl_mechanism,
        sasl_plain_username,
        sasl_plain_password,
        ssl_certfile=None,
        ssl_keyfile=None,
):
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,
        # ssl_check_hostname=self.app.config.get('ssl_check_hostname'],
        ssl_cafile=certifi.where(),
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password,
    )


def get_consumer(
        topic,
        bootstrap_servers,
        security_protocol,
        sasl_mechanism,
        sasl_plain_username,
        sasl_plain_password,
        ssl_certfile=None,
        ssl_keyfile=None,
):
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,
        # ssl_check_hostname = self.app.config.get('ssl_check_hostname'],
        ssl_cafile=certifi.where(),
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password,
    )


class FvhKafkaProducer(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
        self._producer = self.get_producer()

    def init_app(self, app):
        app.config.setdefault("BOOTSTRAP_SERVERS", "localhost:9092")
        app.config.setdefault("SECURITY_PROTOCOL", "PLAINTEXT")

    def get_producer(self):
        return get_producer(
            bootstrap_servers=self.app.config["BOOTSTRAP_SERVERS"].split(","),
            security_protocol=self.app.config.get("SECURITY_PROTOCOL"),
            sasl_mechanism=self.app.config.get("SASL_MECHANISM"),
            sasl_plain_username=self.app.config.get("USERNAME"),
            sasl_plain_password=self.app.config.get("PASSWORD"),
        )

    @property
    def producer(self):
        if self._producer is None:
            self._producer = self.get_producer()
        return self._producer


class FvhKafkaConsumer(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
        self._consumer = self.get_consumer()

    def init_app(self, app):
        app.config.setdefault("BOOTSTRAP_SERVERS", "localhost:9092")
        app.config.setdefault("SECURITY_PROTOCOL", "PLAINTEXT")

    def get_consumer(self):
        return get_consumer(
            topic=self.app.config.get("TOPIC_PARSED_DATA"),
            bootstrap_servers=self.app.config["BOOTSTRAP_SERVERS"].split(","),
            security_protocol=self.app.config.get("SECURITY_PROTOCOL"),
            sasl_mechanism=self.app.config.get("SASL_MECHANISM"),
            sasl_plain_username=self.app.config.get("USERNAME"),
            sasl_plain_password=self.app.config.get("PASSWORD"),
        )

    @property
    def consumer(self):
        if self._consumer is None:
            self._consumer = self.get_consumer()
        return self._consumer
