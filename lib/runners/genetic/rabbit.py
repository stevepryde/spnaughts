"""RabbitMQ manager."""

import json
import socket
from typing import Any, Callable, Dict, Optional, Tuple

import pika


QUEUE_START = "qstart"
QUEUE_STOP = "qstop"


class RabbitDisabledError(Exception):

    pass


class RabbitManager:
    """RabbitMQ manager for setting up and interacting with the queues."""

    def __init__(self, host: str = "", username: str = "", password: str = "") -> None:
        """Create RabbitManager object."""
        self._conn = None  # type: Optional[pika.BlockingConnection]
        self._channel = None  # type: Optional[pika.adapters.blocking_connection.BlockingChannel]

        self.host = host or "localhost"
        self.username = username or "spnaughts"
        self.password = password or "spnaughts"

        self.enabled = True
        self.error = ""
        try:
            self.init_queues()
        except (pika.exceptions.AMQPConnectionError, socket.gaierror) as exc:
            self.enabled = False
            self.error = str(exc)
        return

    @property
    def connection(self) -> pika.BlockingConnection:
        """Get the connection to Rabbit."""
        if not self.enabled:
            raise RabbitDisabledError("Rabbit is disabled")

        if not self._conn:
            credentials = pika.credentials.PlainCredentials(
                username=self.username, password=self.password
            )
            self._conn = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, credentials=credentials)
            )
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
        self.channel.queue_declare(queue=QUEUE_START)

        # Output uses an exchange.
        self.channel.exchange_declare(exchange=QUEUE_STOP, exchange_type="direct")

        # To receive messages from this exchange, the processor must create
        # a custom queue and bind it to the exchange with the specific
        # routing key corresponding to the qid of messages it wants to receive.

        # Only fetch 1 job at a time.
        self.channel.basic_qos(prefetch_count=1)
        return

    def consume_batch_queue(self, func: Callable) -> None:
        """Consume the specified queue."""
        # NOTE: This will block until Ctrl+C is pressed.
        self.channel.basic_consume(queue=QUEUE_START, on_message_callback=func, auto_ack=False)
        self.channel.start_consuming()
        return

    def get_from_output_queue(self, qid: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get next message from queue."""
        qname = "{}-{}".format(QUEUE_STOP, qid)
        method_frame, _, body = self.channel.basic_get(qname)
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

    def put_on_batch_queue(self, body: Dict[str, Any]) -> None:
        """Put the specified dict on the specified queue."""
        self.channel.basic_publish(exchange="", routing_key=QUEUE_START, body=json.dumps(body))
        return

    def put_on_output_exchange(self, qid: str, body: Dict[str, Any]) -> None:
        """Put the specified dict on the output exchange."""
        self.channel.basic_publish(exchange=QUEUE_STOP, routing_key=qid, body=json.dumps(body))
        return

    def create_output_queue(self, qid: str) -> None:
        """Create a queue for receiving processed output."""
        qname = "{}-{}".format(QUEUE_STOP, qid)
        self.channel.queue_declare(queue=qname, exclusive=True)
        self.channel.queue_bind(queue=qname, exchange=QUEUE_STOP, routing_key=qid)
        return

    def delete_output_queue(self, qid: str) -> None:
        """
        Explicitly delete the specified queue.

        These will be deleted automatically once the connection drops, but it's
        nice to clean them up earlier if we can.
        NOTE: Not required when using exclusive queues.
        """
        qname = "{}-{}".format(QUEUE_STOP, qid)
        self.channel.queue_delete(queue=qname)
        return
