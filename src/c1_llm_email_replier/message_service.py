# 
# This file is part of the C1_llm_email_replier distribution (https://github.com/VALAWAI/C1_llm_email_replier).
# Copyright (c) 2022-2026 VALAWAI (https://valawai.eu/).
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import json
import logging
import os
import time
from threading import Thread
from typing import Any, Callable, Optional
from pydantic import BaseModel

import pika


class MessageService:
    """The service to send and receive messages from the RabbitMQ"""

    def __init__(
        self,
        host: str = os.getenv('RABBITMQ_HOST', 'mov-mq'),
        port: int = int(os.getenv('RABBITMQ_PORT', "5672")),
        username: str = os.getenv('RABBITMQ_USERNAME', 'mov'),
        password: str = os.getenv('RABBITMQ_PASSWORD', 'password'),
        max_retries: int = int(os.getenv('RABBITMQ_MAX_RETRIES', "100")),
        retry_sleep_seconds: int = int(os.getenv('RABBITMQ_RETRY_SLEEP', "3")),
    ):
        """Initialize the connection to the RabbitMQ

        Parameters
        ----------
        host : str
            The RabbitMQ server host name. By default uses the environment variable RABBITMQ_HOST
            and if it is not defined uses 'mov-mq'.
        port : int
            The RabbitMQ server port. By default uses the environment variable RABBITMQ_PORT
            and if it is not defined uses '5672'.
        username : str
            The user name of the credential to connect to the RabbitMQ serve. By default uses the environment
            variable RABBITMQ_USERNAME and if it is not defined uses 'mov'.
        password : str
            The password of the credential to connect to the RabbitMQ serve. By default uses the environment
            variable RABBITMQ_PASSWORD and if it is not defined uses 'password'.
        max_retries : int
            The number maximum of tries to create a connection with the RabbitMQ server. By default uses
            the environment variable RABBITMQ_MAX_RETRIES and if it is not defined uses '100'.
        retry_sleep_seconds : int
            The seconds to wait between the tries for create a connection with the RabbitMQ server.
            By default uses the environment variable RABBITMQ_RETRY_SLEEP and if it is not defined uses '3'.
        """
        self.credentials = pika.PlainCredentials(username=username, password=password)
        self.host = host
        self.port = port
        self.listen_connection: Optional[pika.BlockingConnection] = None
        self.listen_channel: Any = None
        self.connection_params = pika.ConnectionParameters(host=self.host, port=self.port, credentials=self.credentials)

        for attempt in range(max_retries):
            try:
                self.listen_connection = pika.BlockingConnection(self.connection_params)
                self.listen_channel = self.listen_connection.channel()
                return
            except (OSError, pika.exceptions.AMQPError):
                logging.warning("Cannot connect to RabbitMQ (attempt %d/%d), retrying...", attempt + 1, max_retries)
                time.sleep(retry_sleep_seconds)

        raise ValueError(f"Cannot connect to RabbitMQ at {host}:{port} after {max_retries} attempts")

    def close(self) -> None:
        """Close the connection."""
        try:
            if self.listen_connection is not None and self.listen_connection.is_open:
                self.listen_connection.close()
        except (OSError, pika.exceptions.AMQPError):
            logging.exception("Cannot close the connection to RabbitMQ")
        except BaseException:
            logging.exception("Unexpected error closing RabbitMQ connection")

    def listen_for(self, queue: str, callback: Callable) -> None:
        """Register a listener on a queue.

        Parameters
        ----------
        queue : str
            The name of the queue to listen.
        callback: method
            The method to call when a message is received.
        """
        self.listen_channel.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
        self.listen_channel.basic_consume(queue=queue, auto_ack=True, on_message_callback=callback)
        logging.debug("Listen for the queue %s", queue)

    def publish_to(self, queue: str, msg: Any) -> None:
        """Publish a message to a queue.

        Parameters
        ----------
        queue : str
            The name of the queue to publish the event.
        msg: object
            The message to send.
        """
        try:
            if isinstance(msg, BaseModel):
                body = msg.model_dump_json()
            else:
                body = json.dumps(msg)

            properties = pika.BasicProperties(content_type='application/json')

            # Create an on-demand connection for publishing
            with pika.BlockingConnection(self.connection_params) as publish_connection:
                with publish_connection.channel() as publish_channel:
                    publish_channel.basic_publish(
                        exchange='',
                        routing_key=queue,
                        body=body,
                        properties=properties,
                    )
            logging.debug("Publish message to the queue %s", queue)

        except (OSError, pika.exceptions.AMQPError):
            logging.exception("Cannot publish a msg in the queue %s", queue)
        except (TypeError, ValueError):
            logging.exception("Cannot publish a msg because the message could not be encoded")

    def start_consuming(self) -> None:
        """Start to consume the messages."""
        try:
            logging.info("Start listening for events")
            self.listen_channel.start_consuming()
        except KeyboardInterrupt:
            logging.info("Stop listening for events")
        except pika.exceptions.AMQPError:
            logging.info("Closed connection")
        except BaseException:
            logging.exception("Consuming messages error.")

    def start_consuming_and_forget(self) -> None:
        """Start consuming messages in a background daemon thread."""
        thread = Thread(target=self.start_consuming, daemon=True)
        thread.start()
