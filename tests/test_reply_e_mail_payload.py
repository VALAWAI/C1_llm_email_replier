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

import unittest
import json
from pydantic_core import from_json

from json_resources import load_reply_e_mail_payload_json
from pydantic import ValidationError

from c1_llm_email_replier.reply_e_mail_payload import ReplyEMailPayload


class TestReplyEMailPayload(unittest.TestCase):
	"""Class to test the reply_e_mail_payload
	"""


	def test_load_json(self):
		"""Test can obtain a reply_e_mail_payload from a json"""

		json_dict = load_reply_e_mail_payload_json()
		reply_e_mail_payload = ReplyEMailPayload.model_validate(json_dict)
		assert len(reply_e_mail_payload.addresses) == 1
		assert reply_e_mail_payload.addresses[0].address_type == "TO"
		assert reply_e_mail_payload.addresses[0].name == "Jon Doe"
		assert reply_e_mail_payload.addresses[0].address == "jon_doe@valawai.eu"
		assert reply_e_mail_payload.subject == "Re: How to create a VALAWAI component?"
		assert reply_e_mail_payload.is_html == False
		assert reply_e_mail_payload.content == "Hi Jane,\n\nYou can find all the information at https://valawai.github.io/docs/\n\nBest regards,\nJon"
		
	def test_save_json(self):
		"""Test can obtain a reply_e_mail_payload from a json"""

		json_dict = load_reply_e_mail_payload_json()
		reply_e_mail_payload = ReplyEMailPayload.model_validate(json_dict)
		json_str = reply_e_mail_payload.model_dump_json()
		json_dict2 = from_json(json_str, allow_partial=True)
		
		assert json_dict == json_dict2

	def test_fail_load_empty_json(self):
		"""Test can not load a treatment from an empty json"""

		error = False
		try:

			treatment = ReplyEMailPayload(**{})
			assert treatment is None

		except ValidationError:
			error = True

		# Can create empty treatment
		assert error

	def test_fail_load_reply_e_mail_payload_without_bad_field_value(self):
		"""Test can not load a reply_e_mail_payload without identifier"""

		error = False
		try:

			json_value = load_reply_e_mail_payload_json()
			json_value['addresses'] = "Bad value"
			payload = ReplyEMailPayload(**json_value)
			assert payload is None

		except ValidationError:
			error = True

		# Can load a change parameters without a bad value
		assert error


if __name__ == '__main__':
    unittest.main()
