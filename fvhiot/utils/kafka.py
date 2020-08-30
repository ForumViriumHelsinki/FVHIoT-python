from kafka import KafkaProducer, KafkaConsumer


# NOTE: arguments are probably about to change

def get_producer(bootstrap_servers, security_protocol,
                 sasl_mechanism, sasl_plain_username, sasl_plain_password):
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,
        # ssl_check_hostname=self.app.config.get('ssl_check_hostname'],
        # ssl_cafile=certifi.where(),
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password
    )


def get_consumer(topic, bootstrap_servers, security_protocol,
                 sasl_mechanism, sasl_plain_username, sasl_plain_password):
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        security_protocol=security_protocol,
        # ssl_check_hostname = self.app.config.get('ssl_check_hostname'],
        # ssl_cafile=certifi.where(),
        sasl_mechanism=sasl_mechanism,
        sasl_plain_username=sasl_plain_username,
        sasl_plain_password=sasl_plain_password
    )


class FvhKafkaProducer(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
        self._producer = self.get_producer()

    def init_app(self, app):
        app.config.setdefault('BOOTSTRAP_SERVERS', 'localhost:9092')
        app.config.setdefault('SECURITY_PROTOCOL', 'PLAINTEXT')

    def get_producer(self):
        return get_producer(
            bootstrap_servers=self.app.config['BOOTSTRAP_SERVERS'].split(','),
            security_protocol=self.app.config.get('SECURITY_PROTOCOL'),
            sasl_mechanism=self.app.config.get('SASL_MECHANISM'),
            sasl_plain_username=self.app.config.get('USERNAME'),
            sasl_plain_password=self.app.config.get('PASSWORD')
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
        app.config.setdefault('BOOTSTRAP_SERVERS', 'localhost:9092')
        app.config.setdefault('SECURITY_PROTOCOL', 'PLAINTEXT')

    def get_consumer(self):
        return get_consumer(
            topic=self.app.config.get('TOPIC_PARSED_DATA'),
            bootstrap_servers=self.app.config['BOOTSTRAP_SERVERS'].split(','),
            security_protocol=self.app.config.get('SECURITY_PROTOCOL'),
            sasl_mechanism=self.app.config.get('SASL_MECHANISM'),
            sasl_plain_username=self.app.config.get('USERNAME'),
            sasl_plain_password=self.app.config.get('PASSWORD')
        )

    @property
    def consumer(self):
        if self._consumer is None:
            self._consumer = self.get_consumer()
        return self._consumer
