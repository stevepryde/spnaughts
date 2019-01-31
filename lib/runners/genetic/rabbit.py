"""RabbitMQ manager."""

import json
from typing import Any, Callable, Dict, Optional, Tuple

import pika


QUEUE_START = "qstart"
QUEUE_STOP = "qstop"


class RabbitDisabledError(Exception):

    pass


class RabbitManager:
    """RabbitMQ manager for setting up and interacting with the queues."""

    def __init__(self) -> None:
        """Create RabbitManager object."""
        self._conn = None  # type: Optional[pika.BlockingConnection]
        self._channel = None  # type: Optional[pika.adapters.blocking_connection.BlockingChannel]

        self.enabled = True
        try:
            self.init_queues()
        except pika.exceptions.AMQPConnectionError:
            self.enabled = False
        return

    @property
    def connection(self) -> pika.BlockingConnection:
        """Get the connection to Rabbit."""
        if not self.enabled:
            raise RabbitDisabledError("Rabbit is disabled")

        if not self._conn:
            self._conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        return self._conn

    @property
    def channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        """Get a channel."""
        if not self.enabled:
            raise RabbitDisabledError("Rabbit is disabled")

        if not self._channel:
            self._channel = self.connection.channel()
        return self._channel

    def init_queues(self) -> None:
        """Initialise all queues."""
        for qname in (QUEUE_START, QUEUE_STOP):
            self.channel.queue_declare(queue=qname)
        self.channel.basic_qos(prefetch_count=1)
        return

    def get_from_queue(self, name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get next message from queue."""
        assert name in [QUEUE_START, QUEUE_STOP], "Unknown queue: {}".format(name)
        method_frame, _, body = self.channel.basic_get(name)
        if not method_frame:
            return None

        try:
            body_dict = json.loads(body)
        except ValueError:
            return None

        return (method_frame.delivery_tag, body_dict)

    def done_message(self, delivery_tag: str) -> None:
        """Mark the specified message as done."""
        self.channel.basic_ack(delivery_tag)
        return

    def put_on_queue(self, name: str, body: Dict[str, Any]) -> None:
        """Put the specified dict on the specified queue."""
        assert name in [QUEUE_START, QUEUE_STOP], "Unknown queue: {}".format(name)
        self.channel.basic_publish(exchange="", routing_key=name, body=json.dumps(body))
        return

    def consume_queue(self, name: str, func: Callable) -> None:
        """Consume the specified queue."""
        assert name in [QUEUE_START, QUEUE_STOP], "Unknown queue: {}".format(name)
        # NOTE: This will block until Ctrl+C is pressed.
        self.channel.basic_consume(queue=name, on_message_callback=func, auto_ack=False)
        self.channel.start_consuming()
        return


# Singleton.
rabbit = RabbitManager()

