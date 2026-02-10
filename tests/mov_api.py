#
# This file is part of the C1_llm_emial_replier distribution
# (https://github.com/VALAWAI/C1_llm_emial_replier).
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
import time
import urllib.parse

import requests


def mov_get_log_message_with(level: str, payload: dict):
	"""Ask to the MOV for a log message with the specified level and payload"""

	url_params = urllib.parse.urlencode(
			{
				'order':'-timestamp',
				'offset':0,
				'limit':100,
				'level':level
			}
		)
	url = f"http://host.docker.internal:8083/v1/logs?{url_params}"
	expected_payload = json.dumps(payload)
	for _i in range(30):

		time.sleep(1)
		response = requests.get(url)
		content = response.json()
		if 'total' in content and content['total'] > 0 and 'logs' in content:

			for log in content['logs']:

				if 'payload' in log and log['payload'] == expected_payload:

					return log

	error_msg = "Not found any log that match the level and payload in the MOV."
	raise AssertionError(error_msg)
