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

import json
import time
import unittest

from c1_llm_email_replier.message_service import MessageService


class TestMessageService(unittest.TestCase):
    """Class to test the service to interact with the rabbitMQ"""

    def setUp(self):
        """Create the message service."""

        self.message_service=MessageService()

    def tearDown(self):
        """Stops the message service."""

        self.message_service.close()

    def test_should_not_initilize_to_an_undefined_server(self):
        """Test that can not register to an undefined server"""

        error=None
        before_test=int(time.time())
        retry_sleep_seconds=1
        max_retries=3
        try:

            MessageService(host='undefined',max_retries=max_retries,retry_sleep_seconds=retry_sleep_seconds)

        except ValueError as e:
            # Ignored
            error=e

        after_test=int(time.time())
        assert error is not None
        expected_test_time=before_test+retry_sleep_seconds*max_retries
        assert abs(expected_test_time-after_test) <= retry_sleep_seconds

    def test_publish_and_listen(self):
        """Test that is publish and listen for messages."""

        queue="Queue_to_test_message_service"
        msgs=[]
        def callback(_ch, _method, _properties, body):
            return msgs.append(body)
        self.message_service.listen_for(queue,callback)
        self.message_service.start_consuming_and_forget()
        msg={
            "id": 1,
            "name": "name"
        }
        self.message_service.publish_to(queue,msg)
        for _i in range(10):

            if len(msgs) != 0:
                break

            time.sleep(1)

        assert len(msgs) == 1
        assert msg == json.loads(msgs[0])

if __name__ == '__main__':
    unittest.main()
