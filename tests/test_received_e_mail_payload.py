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

import unittest

from json_resources import load_received_e_mail_payload_json
from pydantic import ValidationError

from c1_llm_email_replier.received_e_mail_payload import ReceivedEMailPayload


class TestReceivedEMailPayload(unittest.TestCase):
	"""Class to test the received_e_mail_payload
	"""


	def test_load_json(self):
		"""Test can obtain a received_e_mail_payload from a json"""

		json_dict = load_received_e_mail_payload_json()
		received_e_mail_payload = ReceivedEMailPayload(**json_dict)
		assert len(received_e_mail_payload.addresses) == 2
		assert received_e_mail_payload.addresses[0].address_type == "FROM"
		assert received_e_mail_payload.addresses[0].name == "Jon Doe"
		assert received_e_mail_payload.addresses[0].address == "jon_doe@valawai.eu"
		assert received_e_mail_payload.addresses[1].address_type == "TO"
		assert received_e_mail_payload.addresses[1].name == "Jane Doe"
		assert received_e_mail_payload.addresses[1].address == "jane@doe.com"
		assert received_e_mail_payload.subject == "How to create a VALAWAI component?"
		assert received_e_mail_payload.mime_type == "text/plain"
		assert received_e_mail_payload.content == "Hi Jane,\n\nCan you inform me how to create a VALAWAI component\n\nBest regards,\nJon"
		assert received_e_mail_payload.received_at == 1715342664

	def test_allow_define_empty_received_e_mail_payload(self):
		"""Test can create an empty received_e_mail_payload"""

		received_e_mail_payload = ReceivedEMailPayload()
		assert received_e_mail_payload is not None

	def test_load_empty_json(self):
		"""Test can not load a change parameters payload from an empty json"""

		received_e_mail_payload = ReceivedEMailPayload()
		assert received_e_mail_payload is not None

	def test_fail_load_received_e_mail_payload_without_bad_field_value(self):
		"""Test can not load a received_e_mail_payload without identifier"""

		error = False
		try:

			json_value = load_received_e_mail_payload_json()
			json_value['addresses'] = "Bad value"
			payload = ReceivedEMailPayload(**json_value)
			assert payload is None

		except ValidationError:
			error = True

		# Can load a change parameters without a bad value
		assert error


if __name__ == '__main__':
    unittest.main()
