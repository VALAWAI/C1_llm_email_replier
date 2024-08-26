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

import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from C1_llm_email_replier.message_service import MessageService
import re
import time

class TestMessageService(unittest.TestCase):
    """Class to test the service to interact with the rabbitMQ
    """
    
    def setUp(self):
        """Create the message service.
        """
        self.message_service=MessageService(host='host.docker.internal',username='mov',password='password')

    
    def test_should_not_initilize_to_an_undefined_server(self):
        """Test that can not register to an undefined server
        """
        
        error=None
        before_test=int(time.time())
        retry_sleep_seconds=1
        max_retries=3
        try:

            MessageService(host='undefined',max_retries=max_retries,retry_sleep_seconds=retry_sleep_seconds)
            
        except Exception as e:
            # Ignored
            error=e

        after_test=int(time.time())
        assert error != None
        expected_test_time=before_test+retry_sleep_seconds*max_retries
        assert  abs(expected_test_time-after_test) <= retry_sleep_seconds
        