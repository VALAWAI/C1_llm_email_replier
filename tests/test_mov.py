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
from C1_llm_email_replier.mov import MOV
from C1_llm_email_replier.message_service import MessageService
import re
import time
import logging


class TestMOV(unittest.TestCase):
    """Class to test the interaction with the Master Of VALAWAI (MOV)
    """
    
    def setUp(self):
        """Create the mov.
        """
        self.message_service=MessageService(host='host.docker.internal',username='mov',password='password')
        self.mov = MOV(self.message_service)
        
    def tearDown(self):
        """Stops the message service.
        """
        self.message_service.close()
    
    def test_register_component_msg(self):
        """Test the creation of the message to register the component
        """
        msg = self.mov.register_component_msg()
        assert re.match(r'\d+\.\d+\.\d+', msg['version'])
        assert len(msg['asyncapi_yaml'])>100
 
    def test_register_component(self):
        """Test the register of the component
        """
        self.message_service.start_consuming_and_forget()
        self.mov.register_component()
        
        for i in range(10):
            
            if self.mov.registered_id != None:
                break
            
            time.sleep(1)
        
        assert self.mov.registered_id != None
