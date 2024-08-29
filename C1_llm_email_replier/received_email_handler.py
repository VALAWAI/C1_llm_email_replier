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
#

from message_service import MessageService
from mov import MOV
from email_replier_generator import EMailReplierGenerator
import logging
import json
import html2text

class ReceivedEMailHandler(object):
    """The component that handle the messages with the e-mails to reply.
    """
    
    def __init__(self,message_service:MessageService,mov:MOV):
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
        self.message_service.listen_for('valawai/c1/llm_email_replier/data/received_e_mail',self.handle_message)
    
    
    def handle_message(self,ch, method, properties, body):
        """Manage the received messages on the channel valawai/c1/llm_email_replier/data/received_e_mail
        """
        try:
            
            e_mail=json.loads(body)
            self.mov.info("Received an e-mail",e_mail)
            
            reply_address=[]
            if "address" in e_mail:
                
                for address in e_mail["address"]:
                    
                    if 'type' in address and 'address' in address:
                        
                        type=str(address['type'])
                        if type == 'FROM' or type == 'CC' or type == 'BCC':
                        
                            if type == 'FROM':
                                type = 'TO'    
                            
                            reply_to = {
                                "type":type,
                                "address":str(address['address'])
                                }
                    
                            if 'name' in address:
                                reply_to['name']=str(address['name'])
                    
                            reply_address.append(reply_to)
                    
                
            if len(reply_address)== 0:
                
                self.mov.error("No specified the address of the user to reply",e_mail)
                return            
            
            subject="No subject"
            if "subject" in e_mail:
                
                subject=str(e_mail["subject"])

            content="No content"
            if "content" in e_mail:
                
                content=str(e_mail["content"])
                if "mime_type" in e_mail and e_mail["mime_type"] == "text/html":
                    converter = html2text.HTML2Text()
                    converter.ignore_links = True
                    content = converter.handle(content)
            
            
            generator=EMailReplierGenerator()
            reply_subject,reply_content=generator.generate_reply(subject,content)
            
            reply_msg={
               "address": reply_address,
               "subject": reply_subject,
               "is_html": False,
               "content": reply_content
               }
            self.message_service.publish_to('valawai/c1/llm_email_replier/data/reply_e_mail',reply_msg)
            self.mov.info("Sent reply to e-mail",reply_msg)
            
        except Exception:
            
            logging.exception(f"Unexpected message {body}")
