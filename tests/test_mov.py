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
import json


class TestMOV(unittest.TestCase):
    """Class to test the interaction with the Master Of VALAWAI (MOV)
    """
    
    def setUp(self):
        """Create the mov.
        """
        self.message_service=MessageService(host='host.docker.internal',username='mov',password='password')
        self.mov = MOV(self.message_service)
        self.msgs=[]
        
    def tearDown(self):
        """Stops the message service.
        """
        self.mov.unregister_component()
        self.message_service.close()
    
    def test_register_component_msg(self):
        """Test the creation of the message to register the component
        """
        msg = self.mov.register_component_msg()
        assert re.match(r'\d+\.\d+\.\d+', msg['version'])
        assert len(msg['asyncapi_yaml'])>100
        
    def callback(self, ch, method, properties, body):
        """Called when a message is received from a listener.
        """
        try:
            
            logging.debug("Received %s",body)
            msg=json.loads(body)
            self.msgs.append(msg)
            
        except Exception as error:
            print(error)
    
    
    def __assert_registerd(self,component_id):
        """Check that a component is registered.
        """
        for i in range(10):
            
            time.sleep(1)
            self.msgs=[]
            query_id=f"query_assert_registerd_{i}"
            query={
                'id':query_id,
                'type':'C1',
                'pattern':'c1_llm_email_replier',
                'offset':0,
                'limit':1000
            }
            self.message_service.publish_to('valawai/component/query',query)
            for j in range(10):
                
                if len(self.msgs) != 0 and self.msgs[0]['query_id'] == query_id:
                    
                    if self.msgs[0]['total'] > 0:
                        
                        for component in self.msgs[0]['components']:
                        
                            if component['id'] == component_id:
                                return

                    break
                time.sleep(1)
        
        self.fail(f"Component {component_id} is not registered") 

    def __assert_unregisterd(self,component_id):
        """Check that a component is unregistered.
        """
        for i in range(10):
            
            time.sleep(1)
            self.msgs=[]
            query_id=f"query_assert_unregisterd_{i}"
            query={
                'id':query_id,
                'type':'C1',
                'pattern':'c1_llm_email_replier',
                'offset':0,
                'limit':1000
            }
            self.message_service.publish_to('valawai/component/query',query)
            for j in range(10):
                
                if len(self.msgs) != 0 and self.msgs[0]['query_id'] == query_id:
                    
                    found=False
                    if self.msgs[0]['total'] > 0:
                        
                        for component in self.msgs[0]['components']:
                        
                            if component['id'] == component_id:
                                found=True
                                break

                    if found == True:
                        break;
                    else:
                        return

                time.sleep(1)
        
        self.fail(f"Component {component_id} is not unregistered") 
        
 
    def test_register_and_unregister_component(self):
        """Test the register and unregister the component
        """
        
        self.message_service.listen_for('valawai/component/page',self.callback)
        self.message_service.start_consuming_and_forget()
        self.mov.register_component()
        
        
        for i in range(10):
            
            if self.mov.component_id != None:
                break
            
            time.sleep(1)
        
        
        assert self.mov.component_id != None
        component_id=self.mov.component_id
        self.__assert_registerd(component_id)
        
        self.mov.unregister_component()
        self.__assert_unregisterd(component_id)
