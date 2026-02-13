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

import json
import logging
import math
import os
import time
import unittest
import uuid

from mov_api import mov_get_log_message_with

from c1_llm_email_replier.mov import MOV
from c1_llm_email_replier.message_service import MessageService
from c1_llm_email_replier.received_e_mail_handler import ReceivedEMailHandler


class TestReceivedEMailHandler(unittest.TestCase):
    """Class to test the handler of the receiver e-mails to reply
    """
    
    @classmethod
    def setUpClass(cls):
        """Create the handler."""
        
        cls.message_service = MessageService()
        cls.mov = MOV(cls.message_service)
        cls.handler = ReceivedEMailHandler(cls.message_service, cls.mov)
        cls.msgs = []
        cls.message_service.listen_for('valawai/c1/llm_email_replier/data/reply_e_mail', cls.callback)
        cls.message_service.start_consuming_and_forget()
    
    @classmethod
    def tearDownClass(cls):
        """Stops the message service."""
        
        cls.mov.unregister_component()
        cls.message_service.close()
    
    @classmethod
    def callback(cls, _ch, _method, _properties, body):
        """Called when a message is received from a listener."""
        
        try:
        
            logging.debug("Received %s", body)
            msg = json.loads(body)
            cls.msgs.append(msg)
        
        except ValueError:
        
            logging.exception("Unexpected %s", body)
    
    
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

    def test_not_reply_if_not_exist_an_address_to_reply(self):
        """Check that the handler not reply if does not exist an address to reply to
        """
        
        self.message_service.start_consuming_and_forget()
        e_mail = {
            'subject':str(uuid.uuid4())
        }
        self.message_service.publish_to('valawai/c1/llm_email_replier/data/received_e_mail', e_mail)
        
        expected_payload = json.dumps(e_mail)
        for i in range(11):
            
            logs = self.__capture_last_logs_from_mov(2)
            found_info = False
            found_error = False
            for log in logs:
            
                if 'payload' in log and log['payload'] == expected_payload and 'level' in log:
                    
                    if found_info == False and log['level'] == 'INFO':
                    
                        found_info = True
                         
                    elif found_error == False and log['level'] == 'ERROR':
                      
                        found_error = True
                         
                    else:
                        # Unexpected event
                        break
            
            if found_error == True and found_info == True:
                # Found the expected logs
                return
        
        self.fail("Not generated the expected logs to the MOV")
        
    def __assert_publish_and_receive_reply_for(self, e_mail):
        """Publish and e-mail and expect a reply
        
        Parameters
        ----------
        e_mail : object
            The email to receive a reply
            
        Returns
        -------
        object
            The replied e-mail
        """
        
        e_mail_payload = json.dumps(e_mail)
        self.message_service.publish_to('valawai/c1/llm_email_replier/data/received_e_mail', e_mail_payload)
        
        expected_address = []
        for address in e_mail['address']:
            
            if address['type'] != 'TO':
                
                copy = json.loads(json.dumps(address))
                if copy['type'] == 'FROM':
                
                    copy['type'] = 'TO'
                    
                expected_address.append(copy)
        
        last_error: Exception = None
        for i in range(101):
            
            time.sleep(3)
            if len(self.msgs) > 0:
                
                for msg in self.msgs:
                    
                    try:
                    
                        self.assertTrue('address' in msg, "Must have address to reply")
                        self.assertEqual(msg['address'], expected_address)
                    
                        self.assertTrue('subject' in msg, "Must have a subject")
                        self.assertGreater(len(msg['subject']), 0, "The subject can not be empty")
                    
                        if 'subject' in e_mail and msg['subject'].startswith('Re:'):
                        
                            self.assertTrue(msg['subject'].endswith(e_mail['subject']), "The reply subject may have the original subject")
                    
                        self.assertTrue('is_html' in msg, "Must mark if is a html")
                        self.assertFalse(msg['is_html'], "The content may be text/plain")
                    
                        self.assertTrue('content' in msg, "Must have a content")
                        self.assertGreater(len(msg['content']), 0, "The content can not be empty")
                    
                        return msg
                        
                    except Exception as error:

                        last_error = error
            
        self.fail(f"Not received a reply for {e_mail}, because {last_error}")
        
    def __assert_notify_mov_of_reply(self,e_mail,reply):
        """Check that the MOV is notified of the received e-mial and the reply of it.
        
        Parameters
        ----------
        e_mail: object
            The e-mail that will be received
        reply: object
            The replied e-mail
        
        """
        e_mail_payload = json.dumps(e_mail)
        reply_payload = json.dumps(reply)
        for i in range(11):
            
            logs = self.__capture_last_logs_from_mov(2)
            found_info_email = False
            found_info_reply = False
            for log in logs:
            
                if 'payload' in log and 'level' in log and log['level'] == 'INFO':
                    
                    if found_info_email == False and log['payload'] == e_mail_payload:
                    
                        found_info_email = True  
                         
                    elif found_info_reply == False and log['payload'] == reply_payload:
                      
                        found_info_reply = True
            
                    if found_info_email == True and found_info_reply == True:
                        # Found the expected logs
                        return
        
        self.fail("Not generated the expected logs to the MOV")
        
    def test_reply_without_content(self):
        """Check that the handler can reply without content
        """
        
        e_mail = {
            'address':[
                {
                    'type':'FROM',
                    'address':'from@valawai.eu'
                },
                {
                    'type':'TO',
                    'address':'to@valawai.eu'
                },
                {
                    'type':'CC',
                    'address':'cc@valawai.eu'
                },
                {
                    'type':'BCC',
                    'address':'bcc@valawai.eu'
                }
            ],
            'subject':str(uuid.uuid4())
        }
        reply = self.__assert_publish_and_receive_reply_for(e_mail)
        self.__assert_notify_mov_of_reply(e_mail,reply)

    def test_reply_without_subject(self):
        """Check that the handler can reply without subject
        """
        
        e_mail = {
            'address':[
                {
                    'type':'FROM',
                    'address':'from@valawai.eu',
                    'name': 'From'
                },
                {
                    'type':'TO',
                    'address':'to@valawai.eu',
                    'name': 'To'
                },
                {
                    'type':'CC',
                    'address':'cc@valawai.eu',
                    'name': 'Cc'
                },
                {
                    'type':'BCC',
                    'address':'bcc@valawai.eu',
                    'name': 'Bcc'
                }
            ],
            'content':"<p>The product reference is <b>" + str(uuid.uuid4()) + "</b></p>",
            'mime_type': 'text/html'
        }
        reply = self.__assert_publish_and_receive_reply_for(e_mail)
        self.__assert_notify_mov_of_reply(e_mail,reply)

    def test_reply_without_subject_and_content(self):
        """Check that the handler can reply without content
        """
        
        e_mail = {
            'address':[
                {
                    'type':'FROM',
                    'address':'from@valawai.eu',
                    'name': str(uuid.uuid4())
                },
                {
                    'type':'TO',
                    'address':'to@valawai.eu'
                }
            ]
        }
        reply = self.__assert_publish_and_receive_reply_for(e_mail)
        self.__assert_notify_mov_of_reply(e_mail,reply)

    def test_reply_e_mail(self):
        """Check that the handler reply an e-mail
        """
        
        e_mail = {
            'address':[
                {
                    'type':'FROM',
                    'address':'from@valawai.eu',
                    'name': 'Jane Doe'
                },
                {
                    'type':'TO',
                    'address':'to@valawai.eu'
                }
            ],
            'subject':"Order number "+str(uuid.uuid4()),
            'mime_type':'text/plain',
            'content':'Hi!\nThe order referred on the subject has not arrived yet. It is any problem?'
        }
        reply = self.__assert_publish_and_receive_reply_for(e_mail)
        self.__assert_notify_mov_of_reply(e_mail,reply)
