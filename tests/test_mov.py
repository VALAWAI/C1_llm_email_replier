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
import requests
import uuid
import urllib.parse


class TestMOV(unittest.TestCase):
    """Class to test the interaction with the Master Of VALAWAI (MOV)
    """
    
    def setUp(self):
        """Create the mov.
        """
        self.message_service = MessageService(host='host.docker.internal', username='mov', password='password')
        self.mov = MOV(self.message_service)
        self.msgs = []
        
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
        assert len(msg['asyncapi_yaml']) > 100
        
    def callback(self, ch, method, properties, body):
        """Called when a message is received from a listener.
        """
        try:
            
            logging.debug("Received %s", body)
            msg = json.loads(body)
            self.msgs.append(msg)
            
        except Exception as error:
            print(error)
    
    def __assert_registerd(self, component_id):
        """Check that a component is registered.
        """
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
            for j in range(10):
                
                if len(self.msgs) != 0 and self.msgs[0]['query_id'] == query_id:
                    
                    if self.msgs[0]['total'] > 0:
                        
                        for component in self.msgs[0]['components']:
                        
                            if component['id'] == component_id:
                                return

                    break
                time.sleep(1)
        
        self.fail(f"Component {component_id} is not registered") 

    def __assert_unregisterd(self, component_id):
        """Check that a component is unregistered.
        """
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
            for j in range(10):
                
                if len(self.msgs) != 0 and self.msgs[0]['query_id'] == query_id:
                    
                    found = False
                    if self.msgs[0]['total'] > 0:
                        
                        for component in self.msgs[0]['components']:
                        
                            if component['id'] == component_id:
                                found = True
                                break

                    if found == True:
                        break;
                    else:
                        return

                time.sleep(1)
        
        self.fail(f"Component {component_id} is not unregistered") 
 
 
    def __assert_register(self):
        """Assert the component is registered
        """
        self.message_service.start_consuming_and_forget()
        self.mov.register_component()
        
        for i in range(10):
            
            if self.mov.component_id != None:
                break
            
            time.sleep(1)
        
        assert self.mov.component_id != None

    def test_register_and_unregister_component(self):
        """Test the register and unregister the component
        """
        
        self.message_service.listen_for('valawai/component/page', self.callback)
        self.__assert_register()

        component_id = self.mov.component_id
        self.__assert_registerd(component_id)
        
        self.mov.unregister_component()
        self.__assert_unregisterd(component_id)

    def test_debug(self):
        """Check that the component send log messages to the MOV
        """
        
        test_id = "test_debug_" + str(uuid.uuid4())
        self.mov.debug(f"{test_id} empty")
        
        payload = {"index":1}
        self.mov.debug(f"{test_id} with payload", payload)
        
        self.__assert_register()
        self.mov.debug(f"{test_id} empty2")
        
        self.mov.debug(f"{test_id} with payload2", payload)
        url_params = urllib.parse.urlencode(
            {
                'order':'-timestamp',
                'offset':0,
                'limit':10,
                'level':'DEBUG',
                'pattern':f"/{test_id}.+/"
            }
        )
        url = f"http://host.docker.internal:8083/v1/logs?{url_params}"
        logs = []
        for i in range(10):
        
            time.sleep(2)
            response = requests.get(url)
            content = response.json()
            if content['total'] == 4:
                logs = content['logs']
                break
            
        assert len(logs) == 4
        for log in logs:

            assert log['level'] == 'DEBUG'
            type = re.findall(f"{test_id} (.+)", log['message'])[0]
            if type == "empty":
                
                if "payload" in log:
                    assert log['payload'] == None
                if "component" in log:
                    assert log['component'] == None

            elif type == "with payload":
                
                assert log['level'] == 'DEBUG'
                assert json.loads(log['payload']) == payload
                if "component" in log:
                    assert log['component'] == None

            elif type == "empty2":
                
                assert log['level'] == 'DEBUG'
                if "payload" in log:
                    assert log['payload'] == None
                assert log['component']['id'] == self.mov.component_id

            elif type == "with payload2":
                
                assert log['level'] == 'DEBUG'
                assert json.loads(log['payload']) == payload
                assert log['component']['id'] == self.mov.component_id
                
            else:
                self.fail(f"Unexpected {log}")
        
        
