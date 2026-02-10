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

import json
import logging
import os
import re
import time
import unittest
import uuid

from mov_api import mov_get_log_message_with

from c1_llm_email_replier.message_service import MessageService
from c1_llm_email_replier.mov import MOV


class TestMOV(unittest.TestCase):
	"""Class to test the interaction with the Master Of VALAWAI (MOV)"""

	@classmethod
	def setUpClass(cls):
		"""Create the mov."""

		cls.message_service = MessageService()
		cls.mov = MOV(cls.message_service)

	@classmethod
	def tearDownClass(cls):
		"""Stops the message service."""

		cls.mov.unregister_component()
		cls.message_service.close()

	def test_register_component_msg(self):
		"""Test the creation of the message to register the component"""

		msg = self.mov.register_component_msg()
		assert re.match(r'\d+\.\d+\.\d+', msg['version'])
		assert len(msg['asyncapi_yaml']) > 100

	def callback(self, _ch, _method, _properties, body):
		"""Called when a message is received from a listener."""

		try:

			logging.debug("Received %s", body)
			msg = json.loads(body)
			self.msgs.append(msg)

		except ValueError:
			pass

	def __assert_registerd(self, component_id):
		"""Check that a component is registered."""

		found = False
		for i in range(10):

			time.sleep(1)
			self.msgs = []
			query_id = f"query_assert_registerd_{i}"
			query = {
				'id':query_id,
				'type':'C1',
				'pattern':'c1_llm_email_replier',
				'offset':0,
				'limit':1000
			}
			self.message_service.publish_to('valawai/component/query', query)
			for _j in range(10):

				if len(self.msgs) != 0 and self.msgs[0]['query_id'] == query_id:

					if self.msgs[0]['total'] > 0:

						for component in self.msgs[0]['components']:

							if component['id'] == component_id:
								found = True
								break

					break
				time.sleep(1)

		assert found,f"Component {component_id} is not registered"
		log_dir = os.getenv("LOG_DIR","logs")
		component_id_path = os.path.join(log_dir,os.getenv("COMPONET_ID_FILE_NAME","component_id.json"))

		# No stored component_id into a file
		assert os.path.isfile(component_id_path)
		assert os.path.getsize(component_id_path) > 0


	def __assert_unregisterd(self, component_id):
		"""Check that a component is unregistered."""

		found = False
		for i in range(10):

			time.sleep(1)
			self.msgs = []
			query_id = f"query_assert_unregisterd_{i}"
			query = {
				'id':query_id,
				'type':'C1',
				'pattern':'c1_llm_email_replier',
				'offset':0,
				'limit':1000
			}
			self.message_service.publish_to('valawai/component/query', query)
			for _j in range(10):

				if len(self.msgs) != 0 and self.msgs[0]['query_id'] == query_id:

					found = False
					if self.msgs[0]['total'] > 0:

						for component in self.msgs[0]['components']:

							if component['id'] == component_id:
								found = True
								continue


					break

				time.sleep(1)

		assert not found,f"Component {component_id} is not unregistered"
		log_dir = os.getenv("LOG_DIR","logs")
		component_id_path = os.path.join(log_dir,os.getenv("COMPONET_ID_FILE_NAME","component_id.json"))
		assert not os.path.isfile(component_id_path) or os.path.getsize(component_id_path) == 0,"No removed component_id into a file"


	def __assert_register(self):
		"""Assert the component is registered"""

		self.message_service.start_consuming_and_forget()
		self.mov.register_component()

		for _i in range(10):

			if self.mov.component_id is not None:
				break

			time.sleep(1)

		assert self.mov.component_id is not None

	def test_register_and_unregister_component(self):
		"""Test the register and unregister the component"""

		self.msgs = []
		self.message_service.listen_for('valawai/component/page', self.callback)
		self.__assert_register()

		component_id = self.mov.component_id
		self.__assert_registerd(component_id)

		self.mov.unregister_component()
		self.__assert_unregisterd(component_id)

	def test_debug(self):
		"""Check that the component send a DEBUG log messages to the MOV"""

		payload = {"id": str(uuid.uuid4())}
		msg = f"Message of the log {payload['id']}"
		self.mov.debug(msg, payload)
		log = mov_get_log_message_with('DEBUG',payload)
		assert log['message'] == msg

	def test_info(self):
		"""Check that the component send a INFO log messages to the MOV"""

		payload = {"id": str(uuid.uuid4())}
		msg = f"Message of the log {payload['id']}"
		self.mov.info(msg, payload)
		log = mov_get_log_message_with('INFO',payload)
		assert log['message'] == msg

	def test_warn(self):
		"""Check that the component send a WARN log messages to the MOV"""

		payload = {"id": str(uuid.uuid4())}
		msg = f"Message of the log {payload['id']}"
		self.mov.warn(msg, payload)
		log = mov_get_log_message_with('WARN',payload)
		assert log['message'] == msg

	def test_error(self):
		"""Check that the component send a ERROR log messages to the MOV"""

		payload = {"id": str(uuid.uuid4())}
		msg = f"Message of the log {payload['id']}"
		self.mov.error(msg, payload)
		log = mov_get_log_message_with('ERROR',payload)
		assert log['message'] == msg


if __name__ == '__main__':
	unittest.main()