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
from pydantic import BaseModel


def value_to_compare(data):
	"""Normalize a payload value for comparison.

	Accepts a BaseModel, dict, str, bytes, or any other type.
	- BaseModel  → model_dump() dict
	- dict       → returned as-is
	- str/bytes  → decoded and parsed as JSON (falls back to plain string)
	- other      → converted to str, then parsed as JSON (falls back to plain string)
	"""
	if isinstance(data, BaseModel):
		return data.model_dump(by_alias=True)

	if isinstance(data, dict):
		return data

	if isinstance(data, bytes):
		text = data.decode('utf-8')
	elif isinstance(data, str):
		text = data
	else:
		text = str(data)

	try:
		return json.loads(text)
	except Exception:
		return text


def mov_get_log_message_with(level: str, payload: BaseModel | dict | str | bytes):
	"""Ask to the MOV for a log message with the specified level and payload.

	Polls the MOV log API up to 30 times (once per second) until a log entry
	matching the given level and payload is found.

	Parameters
	----------
	level:
		The log level to filter by (e.g. 'ERROR', 'INFO').
	payload:
		The expected payload. Accepts a Pydantic model, dict, JSON string,
		raw bytes, or any other value that can be stringified.

	Returns
	-------
	dict
		The matching log entry.

	Raises
	------
	AssertionError
		If no matching log entry is found within 30 seconds.
	"""
	url_params = urllib.parse.urlencode(
		{
			'order': '-timestamp',
			'offset': 0,
			'limit': 100,
			'level': level,
		}
	)
	url = f"http://host.docker.internal:8083/v1/logs?{url_params}"
	expected = value_to_compare(payload)

	for _i in range(30):
		time.sleep(1)
		response = requests.get(url)
		content = response.json()
		if content.get('total', 0) > 0 and 'logs' in content:
			
			logs = content.get('logs', [])
			for log in logs:
				if 'payload' in log:
					log_payload = value_to_compare(log['payload'])
					if log_payload == expected:
						return log

			print(f"Expected {expected} not in {logs}")

	raise AssertionError("Not found any log that match the level and payload in the MOV.")
