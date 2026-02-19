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
from typing import Any, Union

from c1_llm_email_replier.change_parameters_payload import ChangeParametersPayload
from c1_llm_email_replier.message_service import MessageService
from c1_llm_email_replier.mov import MOV


class ChangeParametersHandler:
    """The component that manage the changes of the component parameters."""

    CONTROL_PARAMETERS_TOPIC = 'valawai/c1/llm_email_replier/control/parameters'

    def __init__(self, message_service: MessageService, mov: MOV):
        """Initialize the handler

        Parameters
        ----------
        message_service : MessageService
                The service to receive or send messages thought RabbitMQ
        mov : MOV
                The service to interact with the MOV
        """
        self.message_service = message_service
        self.mov = mov
        self.message_service.listen_for(self.CONTROL_PARAMETERS_TOPIC, self.handle_message)

    def handle_message(self, _ch, _method, _properties, body: bytes) -> None:
        """Manage the received messages on the channel valawai/c1/llm_email_replier/control/parameters."""

        try:
            json_dict = json.loads(body)

            try:
                parameters = ChangeParametersPayload(**json_dict)
                self._update_parameter(parameters.max_new_tokens, "REPLY_MAX_NEW_TOKENS")
                self._update_parameter(parameters.min_new_tokens, "REPLY_MIN_NEW_TOKENS")
                self._update_parameter(parameters.temperature, "REPLY_TEMPERATURE")
                self._update_parameter(parameters.top_k, "REPLY_TOP_K")
                self._update_parameter(parameters.top_p, "REPLY_TOP_P")
                self._update_parameter(parameters.system_prompt, "REPLY_SYSTEM_PROMPT")

                # Added missing parameters if they are present in the payload
                if hasattr(parameters, 'user_prompt'):
                    self._update_parameter(parameters.user_prompt, "REPLY_USER_PROMPT")
                if hasattr(parameters, 'model_id'):
                    self._update_parameter(parameters.model_id, "LLM_MODEL")

                self.mov.info("Changed the component parameters", json_dict)

            except Exception as validation_error:
                msg = f"Cannot change the parameters, because {validation_error}"
                self.mov.error(msg, json_dict)

        except ValueError:
            logging.exception("Unexpected message %s", body)

    def _update_parameter(self, value: Union[float, str, None], env_property_name: str) -> None:
        """Update a parameter in the environment variables.

        Parameters
        ----------
        value: float | str | None
            The new value for the property.
        env_property_name: str
            The name of the property that contains the parameter.
        """

        if value is not None:
            if isinstance(value, float):
                os.environ[env_property_name] = str(value)
            else:
                os.environ[env_property_name] = str(value)

