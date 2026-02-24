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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <http://www.gnu.org/licenses/>.
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
        self.connection_params = pika.ConnectionParameters(
            host=self.host, 
            port=self.port, 
            credentials=self.credentials,
            heartbeat=int(os.getenv('RABBITMQ_HEARTBEAT', "600")) # Higher heartbeat to survive LLM generation
        )
        self.max_retries = max_retries
        self.retry_sleep_seconds = retry_sleep_seconds
        self.listeners: list[tuple[str, Callable]] = []
        self._stopping = False

        self._connect()

    def _connect(self) -> None:
        """Establish the connection to RabbitMQ with retries."""
        for attempt in range(self.max_retries):
            try:
                if self.listen_connection is not None and self.listen_connection.is_open:
                    return

                self.listen_connection = pika.BlockingConnection(self.connection_params)
                self.listen_channel = self.listen_connection.channel()
                
                # Re-apply listeners if any
                for queue, callback in self.listeners:
                    self._apply_listener(queue, callback)
                
                logging.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
                return
            except (OSError, pika.exceptions.AMQPError) as error:
                logging.warning(f"Cannot connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries}) because {error}. Retrying in {self.retry_sleep_seconds}s...")
                time.sleep(self.retry_sleep_seconds)

        raise ValueError(f"Cannot connect to RabbitMQ at {self.host}:{self.port} after {self.max_retries} attempts")

    def close(self) -> None:
        """Close the connection."""
        self._stopping = True
        try:
            if self.listen_channel is not None and self.listen_channel.is_open:
                self.listen_channel.stop_consuming()
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
        self.listeners.append((queue, callback))
        self._apply_listener(queue, callback)

    def _apply_listener(self, queue: str, callback: Callable) -> None:
        """Actually register the listener on the channel."""
        self.listen_channel.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
        self.listen_channel.basic_consume(queue=queue, auto_ack=True, on_message_callback=callback)
        logging.debug(f"Listen for the queue {queue}")

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
            logging.debug(f"Publish message to the queue {queue}")

        except (OSError, pika.exceptions.AMQPError):
            logging.exception(f"Cannot publish a msg in the queue {queue}")
        except (TypeError, ValueError):
            logging.exception("Cannot publish a msg because the message could not be encoded")

    def start_consuming(self) -> None:
        """Start to consume the messages with automatic reconnection."""
        while not self._stopping:
            try:
                self._connect()
                logging.info(f"Start listening for events on {self.host}:{self.port}")
                self.listen_channel.start_consuming()
            except KeyboardInterrupt:
                logging.info(f"Stop listening for events on {self.host}:{self.port}")
                self.close()
            except (pika.exceptions.AMQPError, pika.exceptions.ConnectionClosedByBroker) as error:
                if self._stopping:
                    break
                logging.warning(f"Connection lost to RabbitMQ at {self.host}:{self.port} ({error}). Reconnecting...")
                self.listen_connection = None # Force reconnection
                time.sleep(self.retry_sleep_seconds)
            except BaseException as error:
                if self._stopping:
                    break
                logging.exception(f"Consuming messages error from RabbitMQ at {self.host}:{self.port} because {error}. Reconnecting...")
                self.listen_connection = None # Force reconnection
                time.sleep(self.retry_sleep_seconds)

    def start_consuming_and_forget(self) -> None:
        """Start consuming messages in a background daemon thread."""
        thread = Thread(target=self.start_consuming, daemon=True)
        thread.start()
