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

from pydantic import BaseModel
import json
import logging
import os.path
from typing import Any, Optional, Dict

from c1_llm_email_replier.message_service import MessageService
from c1_llm_email_replier import __version__


class MOV:
    """The component used to interact with the Master Of VALAWAI (MOV)"""

    def __init__(self, message_service: MessageService):
        """Initialize the connection to the MOV

        Parameters
        ----------
        message_service: MessageService
            The service to receive or send messages thought RabbitMQ
        """
        self.message_service = message_service
        self.component_id: Optional[str] = None
        self.message_service.listen_for('valawai/c1/llm_email_replier/control/registered', self.registered_component)

    def __read_file(self, path: str) -> str:
        """Read a file and return its content."""

        class_file_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(class_file_path, path)
        with open(file_path) as file:
            return file.read()

    def register_component_msg(self) -> Dict[str, Any]:
        """ The message to register this component into the MOV
            (https://valawai.github.io/docs/tutorials/mov#register-a-component)
        """
        async_api = self.__read_file('../../asyncapi.yaml')

        return {
            "type": "C1",
            "name": "c1_llm_email_replier",
            "version": __version__,
            "asyncapi_yaml": async_api
        }

    def register_component(self) -> None:
        """ Register this component into the MOV
            (https://valawai.github.io/docs/tutorials/mov#register-a-component)
        """
        msg = self.register_component_msg()
        self.message_service.publish_to('valawai/component/register', msg)

    def registered_component(self, _ch, _method, _properties, body: bytes) -> None:
        """Called when the component has been registered."""

        logging.debug("Received registered component %s", body)
        msg = json.loads(body)
        self.component_id = msg['id']
        logging.info("Register C1 LLM E-Mail replier with the identifier '%s'", self.component_id)

        try:
            log_dir = os.getenv("LOG_DIR", "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            component_id_path = os.path.join(log_dir, os.getenv("COMPONET_ID_FILE_NAME", "component_id.json"))
            with open(component_id_path, "w") as component_id_file:
                content = json.dumps(msg, sort_keys=True, indent=2)
                component_id_file.write(content)

        except (OSError, ValueError):
            logging.exception("Could not store the component id into a file")

    def unregister_component(self) -> None:
        """ Unregister this component from the MOV
            (https://valawai.github.io/docs/tutorials/mov/#unregister-a-component)
        """
        try:
            log_dir = os.getenv("LOG_DIR", "logs")
            if os.path.exists(log_dir):
                component_id_path = os.path.join(log_dir, os.getenv("COMPONET_ID_FILE_NAME", "component_id.json"))
                if os.path.isfile(component_id_path):
                    os.remove(component_id_path)

        except (OSError, ValueError):
            logging.exception("Could not remove previous component id file")

        if self.component_id is not None:
            msg = {"component_id": self.component_id}
            self.message_service.publish_to('valawai/component/unregister', msg)
            logging.info("Unregister C1 LLM E-Mail replier with the identifier '%s'", self.component_id)
            self.component_id = None

    def debug(self, msg: str, payload: Any = None) -> None:
        """ Send a debug log message to the MOV
            (https://valawai.github.io/docs/tutorials/mov/#add-a-log-message)

        Parameters
        ----------
        msg : str
            The log message
        payload: object
            The payload associated to the log message.
        """
        self.__log('DEBUG', msg, payload)
        logging.debug(msg)

    def info(self, msg: str, payload: Any = None) -> None:
        """ Send a info log message to the MOV
            (https://valawai.github.io/docs/tutorials/mov/#add-a-log-message)

        Parameters
        ----------
        msg : str
            The log message
        payload: object
            The payload associated to the log message.
        """
        self.__log('INFO', msg, payload)
        logging.info(msg)

    def warn(self, msg: str, payload: Any = None) -> None:
        """ Send a warn log message to the MOV
            (https://valawai.github.io/docs/tutorials/mov/#add-a-log-message)

        Parameters
        ----------
        msg : str
            The log message
        payload: object
            The payload associated to the log message.
        """
        self.__log('WARN', msg, payload)
        logging.warning(msg)

    def error(self, msg: str, payload: Any = None) -> None:
        """ Send a error log message to the MOV
            (https://valawai.github.io/docs/tutorials/mov/#add-a-log-message)

        Parameters
        ----------
        msg : str
            The log message
        payload: object
            The payload associated to the log message.
        """
        self.__log('ERROR', msg, payload)
        logging.error(msg)

    def __log(self, level: str, msg: str, payload: Any = None) -> None:
        """ Send a log message to the MOV
            (https://valawai.github.io/docs/tutorials/mov/#add-a-log-message)

        Parameters
        ----------
        level : str
            The log level (DEBUG, INFO, WARN, ERROR)
        msg : str
            The log message
        payload: object, optional
            The payload associated with the log message.
        """

        # MOV treats {…} as template placeholders, so we strip braces from the message
        # to prevent accidental placeholder expansion or errors on the MOV side.
        safe_msg = msg.replace("{", "[").replace("}", "]")
        add_log_payload = {"level": level, "message": safe_msg}

        if payload is not None:
            if isinstance(payload, BaseModel):
                add_log_payload["payload"] = payload.model_dump_json()
            elif isinstance(payload, (dict, list)):
                add_log_payload["payload"] = json.dumps(payload)
            elif isinstance(payload, bytes):
                add_log_payload["payload"] = payload.decode('utf-8', errors='replace')
            elif isinstance(payload, str):
                add_log_payload["payload"] = payload
            else:
                try:
                    add_log_payload["payload"] = json.dumps(payload)
                except (TypeError, ValueError):
                    logging.debug("Could not serialize payload to JSON; falling back to str()")
                    add_log_payload["payload"] = str(payload)

        if self.component_id is not None:
            add_log_payload["component_id"] = self.component_id

        self.message_service.publish_to('valawai/log/add', add_log_payload)
