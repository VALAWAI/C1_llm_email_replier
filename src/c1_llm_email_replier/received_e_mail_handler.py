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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <http://www.gnu.org/licenses/>.
#

import os
import json
from typing import List
import html2text
from concurrent.futures import ThreadPoolExecutor

from c1_llm_email_replier.message_service import MessageService
from c1_llm_email_replier.mov import MOV
from c1_llm_email_replier.email_replier_generator import EMailReplierGenerator
from c1_llm_email_replier.received_e_mail_payload import ReceivedEMailPayload
from c1_llm_email_replier.received_e_mail_address_payload import ReceivedEMailAddressType
from c1_llm_email_replier.reply_e_mail_payload import ReplyEMailPayload
from c1_llm_email_replier.reply_e_mail_address_payload import ReplyEMailAddressType, ReplyEMailAddressPayload


class ReceivedEMailHandler:
    """The component that handle the messages with the e-mails to reply.
    """

    RECEIVED_EMAIL_TOPIC = 'valawai/c1/llm_email_replier/data/received_e_mail'
    REPLY_EMAIL_TOPIC = 'valawai/c1/llm_email_replier/data/reply_e_mail'

    def __init__(self, message_service: MessageService, mov: MOV):
        """Initialize the handler

        Parameters
        ----------
        message_service : MessageService
                The service to receive or send messages thought RabbitMQ
        mov : MOV
                The service to interact with the MOV
        """
        self.message_service = message_service
        self.mov = mov
        self.generator = EMailReplierGenerator()
        
        # Use a thread pool to process messages off-thread
        # this prevents the LLM generation from blocking the RabbitMQ heartbeat
        max_workers = int(os.getenv('REPLY_MAX_WORKERS', '1'))
        if max_workers < 1:
            max_workers = 1
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        self.message_service.listen_for(self.RECEIVED_EMAIL_TOPIC, self.handle_message)

    def handle_message(self, ch, method, properties, body: bytes) -> None:
        """Receive RabbitMQ messages and offload them to the executor thread."""
        self.executor.submit(self._handle_message_task, body)

    def _handle_message_task(self, body: bytes) -> None:
        """Manage the received messages on the channel valawai/c1/llm_email_replier/data/received_e_mail
        """

        try:
            # Handle potential double-encoding from RabbitMQ/Pika
            try:
                # model_validate_json handles bytes or single-encoded JSON strings
                e_mail = ReceivedEMailPayload.model_validate_json(body)
            except Exception:
                # Fallback: if body is double-encoded, it might be a JSON string inside a JSON string
                data = json.loads(body)
                if isinstance(data, str):
                    data = json.loads(data)
                e_mail = ReceivedEMailPayload.model_validate(data)

            self.mov.info("Received an e-mail", e_mail)

            # Map received addresses to reply addresses
            reply_addresses: List[dict] = []
            for addr in e_mail.addresses:
                # We skip TO addresses from the original email as they are likely the component's own address
                if addr.address_type == ReceivedEMailAddressType.TO:
                    continue

                # Map Original Address Type -> Reply Address Type
                # FROM in original email becomes TO in the reply
                # CC and BCC stay the same
                reply_type = ReplyEMailAddressType.TO
                if addr.address_type == ReceivedEMailAddressType.CC:
                    reply_type = ReplyEMailAddressType.CC
                elif addr.address_type == ReceivedEMailAddressType.BCC:
                    reply_type = ReplyEMailAddressType.BCC

                reply_to = ReplyEMailAddressPayload(
                    type=reply_type,
                    address=addr.address,
                    name=addr.name
                ).model_dump()
                reply_addresses.append(reply_to)

            if not reply_addresses:
                self.mov.error("No valid addresses found to reply to", e_mail)
                return

            # Prepare content for generation
            subject = e_mail.subject or "No subject"
            content = e_mail.content or "No content"

            # Convert HTML to Markdown if necessary
            if e_mail.mime_type == "text/html":
                converter = html2text.HTML2Text()
                converter.ignore_links = True
                content = converter.handle(content)

            # Generate the reply
            self.generator.refresh_parameters()
            reply_subject, reply_content = self.generator.generate_reply(subject, content)

            # Construct and send the reply payload
            reply_msg = ReplyEMailPayload(
                addresses=reply_addresses,
                subject=reply_subject,
                is_html=False,
                content=reply_content
            )
            self.message_service.publish_to(self.REPLY_EMAIL_TOPIC, reply_msg)
            self.mov.info("Sent e-mail reply", reply_msg)

        except Exception as error:
            # Enhanced error logging with body snippet
            body_snippet = body[:100].decode('utf-8', errors='replace') if body else "None"
            msg = f"Failed to process message: {error}. Body start: {body_snippet}..."
            self.mov.error(msg, body)