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

import json
from typing import Any, List
import html2text

from .message_service import MessageService
from .mov import MOV
from .email_replier_generator import EMailReplierGenerator
from .received_e_mail_payload import ReceivedEMailPayload
from .received_e_mail_address_payload import ReceivedEMailAddressType
from .reply_e_mail_payload import ReplyEMailPayload
from .reply_e_mail_address_payload import ReplyEMailAddressType, ReplyEMailAddressPayload


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
        self.message_service.listen_for(self.RECEIVED_EMAIL_TOPIC, self.handle_message)

    def handle_message(self, _ch, _method, _properties, body: bytes) -> None:
        """Manage the received messages on the channel valawai/c1/llm_email_replier/data/received_e_mail
        """

        try:
            # Handle potential double-encoding from Pika
            try:
                # model_validate_json handles bytes or single-encoded strings
                e_mail = ReceivedEMailPayload.model_validate_json(body)
            except Exception:
                # If it fails, the body might be a double-encoded string
                data = json.loads(body)
                if isinstance(data, str):
                    data = json.loads(data)
                e_mail = ReceivedEMailPayload.model_validate(data)

            self.mov.info("Received an e-mail", e_mail)

            reply_addresses: list[dict] = []
            for address in e_mail.addresses:
                # address_type is a ReceivedEMailAddressType Enum
                if address.address_type is not None and address.address is not None:
                    # Use .value for string comparison if needed, or compare to Enum members
                    if address.address_type != ReceivedEMailAddressType.TO:

                        address_type = ReplyEMailAddressType.TO
                        if address.address_type == ReceivedEMailAddressType.BCC:
                            address_type = ReplyEMailAddressType.BCC
                        elif address.address_type == ReceivedEMailAddressType.CC:
                            address_type = ReplyEMailAddressType.CC

                        reply_to = ReplyEMailAddressPayload(**{
                            "type": address_type,
                            "address": address.address,
                            "name": address.name
                        }).model_dump()
                        reply_addresses.append(reply_to)

            if len(reply_addresses) == 0:
                self.mov.error("No specified the address of the user to reply", e_mail)
                return

            # Access attributes via dot notation, not dictionary keys
            subject = e_mail.subject if e_mail.subject is not None else "No subject"
            content = e_mail.content if e_mail.content is not None else "No content"

            if e_mail.mime_type == "text/html":
                converter = html2text.HTML2Text()
                converter.ignore_links = True
                content = converter.handle(content)

            self.generator.refresh_parameters()
            reply_subject, reply_content = self.generator.generate_reply(subject, content)
            reply_msg = ReplyEMailPayload(**{
                "addresses": reply_addresses,
                "subject": reply_subject,
                "is_html": False,
                "content": reply_content
            })
            self.message_service.publish_to(self.REPLY_EMAIL_TOPIC, reply_msg)
            self.mov.info("Sent reply to e-mail", reply_msg)

        except Exception as error:
            msg = f"Cannot process the received message, because {error}"
            self.mov.error(msg, body)