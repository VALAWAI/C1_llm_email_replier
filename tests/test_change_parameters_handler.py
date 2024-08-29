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
from _ast import Or
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from C1_llm_email_replier.mov import MOV
from C1_llm_email_replier.message_service import MessageService
from C1_llm_email_replier.change_parameters_handler import ChangeParametersHandler
import re
import time
import logging
import json
import requests
import uuid
import urllib.parse
import random


class TestChangeParametersHandler(unittest.TestCase):
    """Class to test the handler of the receiver e-mails to reply
    """
    
    def setUp(self):
        """Create the handler.
        """
        self.message_service = MessageService(host='host.docker.internal', username='mov', password='password')
        self.mov = MOV(self.message_service)
        self.msgs = []
        self.handler = ChangeParametersHandler(self.message_service, self.mov)
        
    def tearDown(self):
        """Stops the message service.
        """
        self.mov.unregister_component()
        self.message_service.close()
    
    def callback(self, ch, method, properties, body):
        """Called when a message is received from a listener.
        """
        try:
            
            logging.debug("Received %s", body)
            msg = json.loads(body)
            self.msgs.append(msg)
            
        except Exception as error:
            print(error)
    
    def test_capture_bad_json_message_body(self):
        """Check that the handler can manage when the body is not a valid json
        """
        
        with self.assertLogs() as cm:
            
            self.handler.handle_message(None, None, None, "{")
            
        self.assertEqual(1, len(cm.output))
        self.assertRegex(cm.output[0], r'Unexpected message \{')
        
    def __capture_last_logs_from_mov(self, min:int=1):
        """Capture the last logs messages provided in the MOV
        """
        
        url_params = urllib.parse.urlencode(
            {
                'order':'-timestamp',
                'offset':0,
                'limit':100
            }
        )
        url = f"http://host.docker.internal:8083/v1/logs?{url_params}"
        for i in range(10):
        
            time.sleep(2)
            response = requests.get(url)
            content = response.json()
            if 'total' in content and content['total'] >= min and 'logs' in content:
                return content['logs']
            
        self.fail("Could not get the logs from the MOV") 

    def __assert_process_change_parameters(self, level:str, parameters):
        """Check that
        
        Parameters
        ----------
        level: str
            The expected level of the message when the parameters are changed
        parameters: object
            The parameters that can not be set
        """
        self.message_service.start_consuming_and_forget()
        self.message_service.publish_to('valawai/c1/llm_email_replier/control/parameters', parameters)
        
        expected_payload = json.dumps(parameters)
        for i in range(11):
            
            logs = self.__capture_last_logs_from_mov(2)
            for log in logs:
            
                if 'payload' in log and log['payload'] == expected_payload and 'level' in log and log['level'] == level:
                    # Found the expected log
                    return
        
        self.fail("Not generated the expected logs to the MOV")

    def test_not_change_max_new_tokens_with_a_bad_value(self):
        """Check that the handler not change the 'max_new_tokens' when it is not valid
        """
        
        parameters = {
            'max_new_tokens':str(uuid.uuid4())
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_max_new_tokens_with_a_value_less_than_100(self):
        """Check that the handler not change the 'max_new_tokens' if the value is less than 100
        """
        
        parameters = {
            'max_new_tokens':random.randrange(0, 99, 1)
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_max_new_tokens_with_a_value_more_than_1000(self):
        """Check that the handler not change the 'max_new_tokens' if the value is more than 1000
        """
        
        parameters = {
            'max_new_tokens':random.randrange(1001, 2000, 1)
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_change_max_new_tokens(self):
        """Check that the handler change the 'max_new_tokens'
        """
        
        max_new_tokens = 256 + random.randrange(11, 111, 1)
        parameters = {
            'max_new_tokens':max_new_tokens
        }
        self.__assert_process_change_parameters('INFO', parameters)
        self.assertEqual(str(max_new_tokens), os.getenv("REPLY_MAX_NEW_TOKENS"))

    def test_not_change_temperature_with_a_bad_value(self):
        """Check that the handler not change the 'temperature' when it is not valid
        """
        
        parameters = {
            'temperature':str(uuid.uuid4())
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_temperature_with_a_value_less_than_0(self):
        """Check that the handler not change the 'temperature' if the value is less than 0
        """
        
        parameters = {
            'temperature':-1 * random.random()
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_temperature_with_a_value_more_than_1(self):
        """Check that the handler not change the 'temperature' if the value is more than 1
        """
        
        parameters = {
            'temperature':1.0000001 + random.random()
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_change_temperture(self):
        """Check that the handler change the 'temperature'
        """
        
        temperature = 0.7 + 0.001 * random.randrange(1, 99, 1)
        print(temperature)
        parameters = {
            'temperature':temperature
        }
        self.__assert_process_change_parameters('INFO', parameters)
        self.assertEqual(str(temperature), os.getenv("REPLY_TEMPERATURE"))

    def test_not_change_top_k_with_a_bad_value(self):
        """Check that the handler not change the 'top_k' when it is not valid
        """
        
        parameters = {
            'top_k':str(uuid.uuid4())
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_top_k_with_a_value_less_than_1(self):
        """Check that the handler not change the 'top_k' if the value is less than 1
        """
        
        parameters = {
            'top_k':-1 * random.randrange(0, 100, 1)
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_top_k_with_a_value_more_than_100(self):
        """Check that the handler not change the 'top_k' if the value is more than 100
        """
        
        parameters = {
            'top_k':random.randrange(101, 200, 1)
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_change_top_k(self):
        """Check that the handler change the 'top_k'
        """
        
        top_k = 40 + random.randrange(1, 21, 1)
        parameters = {
            'top_k':top_k
        }
        self.__assert_process_change_parameters('INFO', parameters)
        self.assertEqual(str(top_k), os.getenv("REPLY_TOP_K"))

    def test_not_change_top_p_with_a_bad_value(self):
        """Check that the handler not change the 'top_p' when it is not valid
        """
        
        parameters = {
            'top_p':str(uuid.uuid4())
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_top_p_with_a_value_less_than_0(self):
        """Check that the handler not change the 'top_p' if the value is less than 0
        """
        
        parameters = {
            'top_p':-1 * random.random()
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_top_p_with_a_value_more_than_1(self):
        """Check that the handler not change the 'top_p' if the value is more than 1
        """
        
        parameters = {
            'top_p':1.0000001 + random.random()
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_change_top_p(self):
        """Check that the handler change the 'top_p'
        """
        
        top_p = 0.9 + 0.001 * random.randrange(1, 99, 1)
        parameters = {
            'top_p':top_p
        }
        self.__assert_process_change_parameters('INFO', parameters)
        self.assertEqual(str(top_p), os.getenv("REPLY_TOP_P"))

    def test_not_change_system_prompt_with_a_value_less_than_10(self):
        """Check that the handler not change the 'system_prompt' if the value is less than 10 characters
        """
        
        parameters = {
            'system_prompt':"".join(map(chr, (ord('a')+(y%26) for y in range(9))))
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_not_change_system_prompt_with_a_value_more_than_10000(self):
        """Check that the handler not change the 'system_prompt' if the value is more than 10000 characters
        """
        
        parameters = {
            'system_prompt':"".join(map(chr, (ord('a')+(y%26) for y in range(100001))))
        }
        self.__assert_process_change_parameters('ERROR', parameters)

    def test_change_system_prompt(self):
        """Check that the handler change the 'system_prompt'
        """
        
        system_prompt = 'You are a polite email replier who used as contact info the e-mail ' + str(uuid.uuid4()) + '@valawai.eu'
        parameters = {
            'system_prompt':system_prompt
        }
        self.__assert_process_change_parameters('INFO', parameters)
        self.assertEqual(system_prompt, os.getenv("REPLY_SYSTEM_PROMPT"))
        
    def test_change_parameters(self):
        """Check that the handler change the parameters
        """
        
        max_new_tokens = 256 + random.randrange(11, 111, 1)
        temperature = 0.7 + 0.001 * random.randrange(1, 100, 1)
        top_k = 40 + random.randrange(1, 21, 1)
        top_p = 0.9 + 0.001 * random.randrange(1, 99, 1)
        system_prompt = 'You are a polite email replier who used as contact info the e-mail ' + str(uuid.uuid4()) + '@valawai.eu'
        parameters = {
            'max_new_tokens':max_new_tokens,
            'temperature':temperature,
            'top_k':top_k,
            'top_p':top_p,
            'system_prompt':system_prompt
        }
        self.__assert_process_change_parameters('INFO', parameters)
        self.assertEqual(str(max_new_tokens), os.getenv("REPLY_MAX_NEW_TOKENS"))
        self.assertEqual(str(temperature), os.getenv("REPLY_TEMPERATURE"))
        self.assertEqual(str(top_k), os.getenv("REPLY_TOP_K"))
        self.assertEqual(str(top_p), os.getenv("REPLY_TOP_P"))
        self.assertEqual(system_prompt, os.getenv("REPLY_SYSTEM_PROMPT"))
