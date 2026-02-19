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

import logging
import time
import unittest
import uuid
import os
from unittest.mock import patch, MagicMock

from mov_api import mov_get_log_message_with

from c1_llm_email_replier.mov import MOV
from c1_llm_email_replier.message_service import MessageService
from c1_llm_email_replier.received_e_mail_handler import ReceivedEMailHandler
from c1_llm_email_replier.received_e_mail_payload import ReceivedEMailPayload
from c1_llm_email_replier.received_e_mail_address_payload import ReceivedEMailAddressType
from c1_llm_email_replier.reply_e_mail_payload import ReplyEMailPayload
from c1_llm_email_replier.reply_e_mail_address_payload import ReplyEMailAddressType


class BaseTestReceivedEMailHandler(unittest.TestCase):
    """Base class providing shared setup and helper methods for ReceivedEMailHandler tests."""

    RECEIVED_TOPIC = 'valawai/c1/llm_email_replier/data/received_e_mail'
    REPLY_TOPIC = 'valawai/c1/llm_email_replier/data/reply_e_mail'

    def setUp(self):
        """Clear received messages before each test."""
        if hasattr(self, 'msgs'):
            self.msgs.clear()

    @classmethod
    def callback(cls, _ch, _method, _properties, body):
        """Append each received reply message to the shared list."""
        try:
            if isinstance(body, bytes):
                text = body.decode('utf-8')
            elif isinstance(body, str):
                text = body
            else:
                text = str(body)
            msg = ReplyEMailPayload.model_validate_json(text)
            cls.msgs.append(msg)
            logging.info(f"Received message: {msg}")

        except ValueError:
            logging.error(f"Unexpected body: {body}")

    def _verify_reply_addresses(self, e_mail: ReceivedEMailPayload, msg: ReplyEMailPayload):
        """Verify that the reply has correct addresses mapped from the original e-mail."""
        self.assertIsNotNone(msg.addresses, "Reply must have addresses")
        
        for address in e_mail.addresses:
            if address.address_type == ReceivedEMailAddressType.TO:
                continue
            
            expected_type = ReplyEMailAddressType.TO
            if address.address_type == ReceivedEMailAddressType.CC:
                expected_type = ReplyEMailAddressType.CC
            elif address.address_type == ReceivedEMailAddressType.BCC:
                expected_type = ReplyEMailAddressType.BCC
            elif address.address_type != ReceivedEMailAddressType.FROM:
                continue

            found = any(
                address.address == reply_address.address and reply_address.address_type == expected_type
                for reply_address in msg.addresses
            )
            self.assertTrue(found, f"Expected {expected_type} address {address.address} not found in reply")

    def _verify_reply_content(self, e_mail: ReceivedEMailPayload, msg: ReplyEMailPayload):
        """Verify subject, content and mime type of the reply."""
        self.assertIsNotNone(msg.subject, "Reply must have a subject")
        self.assertGreater(len(msg.subject), 0, "Reply subject must not be empty")

        if e_mail.subject and msg.subject.startswith('Re:'):
            self.assertTrue(
                msg.subject.endswith(e_mail.subject),
                f"Reply subject '{msg.subject}' should end with original subject '{e_mail.subject}'",
            )

        self.assertIsNotNone(msg.is_html, "Reply must declare is_html")
        self.assertFalse(msg.is_html, "Reply content must be text/plain")
        self.assertIsNotNone(msg.content, "Reply must have content")
        self.assertGreater(len(msg.content), 0, "Reply content must not be empty")


class TestReceivedEMailHandlerUnit(BaseTestReceivedEMailHandler):
    """Unit tests for ReceivedEMailHandler using a mocked generator and mocked services."""

    def setUp(self):
        super().setUp()
        self.mock_message_service = MagicMock(spec=MessageService)
        self.mock_mov = MagicMock(spec=MOV)
        
        with patch('c1_llm_email_replier.received_e_mail_handler.EMailReplierGenerator') as mock_gen_class:
            self.mock_generator = mock_gen_class.return_value
            self.handler = ReceivedEMailHandler(self.mock_message_service, self.mock_mov)
        
        # Configure standard mock behavior
        self.mock_generator.generate_reply.return_value = ("Re: Test", "Default reply content")

    def test_capture_message_without_addresses(self):
        """Handler should log an ERROR when the received e-mail has no valid addresses."""
        e_mail_data = {'subject': str(uuid.uuid4())}
        body = json.dumps(e_mail_data).encode('utf-8') if 'json' in globals() else str(e_mail_data).encode('utf-8')
        
        # We need to manually call the handle_message with the body
        # Since it's a unit test, we don't publish to a real topic
        import json
        self.handler.handle_message(None, None, None, json.dumps(e_mail_data).encode('utf-8'))
        
        self.mock_mov.error.assert_called()

    def test_not_reply_if_not_exist_an_address_to_reply(self):
        """Handler should log an ERROR when there is no FROM or CC/BCC address to reply to."""
        e_mail = ReceivedEMailPayload(**
            {
                'subject': str(uuid.uuid4()),
                'addresses': [{'type': 'TO', 'address': 'jabe@doe.eu'}]
            }
        )
        self.handler.handle_message(None, None, None, e_mail.model_dump_json().encode('utf-8'))
        self.mock_mov.error.assert_called()

    def test_reply_logic_with_mocked_gen(self):
        """Standard reply test with mocked generator (unit test)."""
        e_mail = ReceivedEMailPayload(**
            {
                'subject': "Test Subject",
                'content': "Test Body",
                'addresses': [{'type': 'FROM', 'address': 'from@valawai.eu'}]
            }
        )
        
        self.handler.handle_message(None, None, None, e_mail.model_dump_json().encode('utf-8'))
        
        self.mock_generator.generate_reply.assert_called_once()
        self.mock_message_service.publish_to.assert_called_once()


class TestReceivedEMailHandlerIntegration(BaseTestReceivedEMailHandler):
    """Integration tests for ReceivedEMailHandler using the real generator and real services."""

    @classmethod
    def setUpClass(cls):
        # Set a small model for testing
        os.environ['LLM_MODEL'] = os.getenv('INTEGRATION_TEST_MODEL', "facebook/opt-125m")
        cls.message_service = MessageService()
        cls.mov = MOV(cls.message_service)
        cls.msgs: list[ReplyEMailPayload] = []
        cls.message_service.listen_for(BaseTestReceivedEMailHandler.REPLY_TOPIC, cls.callback)
        cls.handler = ReceivedEMailHandler(cls.message_service, cls.mov)
        cls.message_service.start_consuming_and_forget()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.mov.unregister_component()
        cls.message_service.close()
        time.sleep(1)
        # Restore environment variables
        os.environ['LLM_MODEL'] = "HuggingFaceH4/zephyr-7b-beta"
        os.environ['REPLY_MAX_NEW_TOKENS'] = "256"
        os.environ['REPLY_MIN_NEW_TOKENS'] = "0"
        os.environ['REPLY_TEMPERATURE'] = "0.7"

    def setUp(self):
        super().setUp()
        self.msgs.clear()

    def _assert_publish_and_receive_reply_for(self, e_mail: ReceivedEMailPayload, timeout: float = 30.0) -> ReplyEMailPayload:
        """Publish an e-mail and wait for a matching reply."""
        self.message_service.publish_to(self.RECEIVED_TOPIC, e_mail.model_dump_json())
        mov_get_log_message_with('INFO', e_mail)

        start_time = time.time()
        last_error: Exception | None = None
        
        while time.time() - start_time < timeout:
            for msg in list(self.msgs):
                try:
                    self._verify_reply_addresses(e_mail, msg)
                    self._verify_reply_content(e_mail, msg)
                    return msg
                except Exception as error:
                    last_error = error
            time.sleep(0.5)

        self.fail(f"No valid reply received for {e_mail!r} within {timeout}s. Last error: {last_error}")

    def test_reply_e_mail_integration(self):
        """Fully integrated test with a real (but small) LLM."""
        e_mail = ReceivedEMailPayload(**
            {
                'subject': "Order " + str(uuid.uuid4()),
                'mime_type': 'text/plain',
                'content': 'Hi! Is there any problem?',
                'addresses': [
                    {'type': 'FROM', 'address': 'from@valawai.eu', 'name': 'Jane Doe'},
                    {'type': 'TO',   'address': 'to@valawai.eu'}
                ]
            }   
        )
        msg = self._assert_publish_and_receive_reply_for(e_mail, timeout=60.0)
        mov_get_log_message_with('INFO', msg)


if __name__ == "__main__":
    unittest.main()
