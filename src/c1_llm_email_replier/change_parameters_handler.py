# 
# This file is part of the C1_llm_emial_replier distribution (https://github.com/VALAWAI/C1_llm_email_replier).
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

from change_parameters_payload import ChangeParametersPayload
from message_service import MessageService
from mov import MOV

class ChangeParametersHandler:
	"""The component that manage the changes of the component parameters."""

	def __init__(self,message_service:MessageService,mov:MOV):
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
		self.message_service.listen_for('valawai/c1/llm_email_replier/control/parameters',self.handle_message)


	def handle_message(self, _ch, _method, _properties, body):
		"""Manage the received messages on the channel valawai/c1/llm_email_replier/control/parameters."""

		try:

			json_dict = json.loads(body)

			try:

				parameters = ChangeParametersPayload(**json_dict)
				self.__update_weight(parameters.max_new_tokens,"REPLY_MAX_NEW_TOKENS")
				self.__update_weight(parameters.temperature,"REPLY_TEMPERATURE")
				self.__update_weight(parameters.top_k,"REPLY_TOP_K")
				self.__update_weight(parameters.top_p,"REPLY_TOP_P")
				self.__update_weight(parameters.system_prompt,"REPLY_SYSTEM_PROMPT")

				self.mov.info("Changed the component parameters",json_dict)

			except ValueError as validation_error:

				msg = f"Cannot change the parameters, because {validation_error}"
				self.mov.error(msg,json_dict)

		except ValueError:

			logging.exception("Unexpected message %s",body)

	def __update_weight(self,value:float|str|None,env_property_name:str):
		"""Update a weight that is used on the justice value alignment calculus.

		Parameters
		----------
		value: float | str | None
			The new value for the property.
		env_property_name: str
			The name of the property that contains the parameter.
		"""

		if value is not None:

			if type(value) == float:
				
				os.environ[env_property_name] = str(value)
				
			else:
				
				os.environ[env_property_name] = value

