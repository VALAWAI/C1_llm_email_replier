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
import os

class ChangeParametersHandler(object):
    """The component that manage the changes of the component parameters.
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
        self.message_service.listen_for('valawai/c1/llm_email_replier/control/parameters',self.handle_message)
    
    
    def handle_message(self,ch, method, properties, body):
        """Manage the received messages on the channel valawai/c1/llm_email_replier/control/parameters
        """
        try:
            
            parameters=json.loads(body)
            
            if 'max_new_tokens' in parameters:
                try:
                
                    max_new_tokens=int(parameters['max_new_tokens'])
                    if max_new_tokens < 100:
                        
                        self.mov.error("Cannot set less than one hundred tokens.",parameters)
                        return
                    
                    elif max_new_tokens > 1000:
                        
                        self.mov.error("Cannot set more than one thousand tokens.",parameters)
                        return
                    
                    else:
                        
                        os.environ["REPLY_MAX_NEW_TOKENS"]=str(max_new_tokens)
                
                except Exception as error:
                    self.mov.error(f"Cannot change the 'max_new_tokens', because {error}",parameters)
                    return
            
            if 'temperature' in parameters:
                try:
                
                    temperature=float(parameters['temperature'])
                    if temperature < 0.0:
                        
                        self.mov.error("Cannot set a temperature less than '0.0'.",parameters)
                        return
                    
                    elif temperature > 1.0:
                        
                        self.mov.error("Cannot set a temperature higher than '1.0'.",parameters)
                        return
                    
                    else:

                        os.environ["REPLY_TEMPERATURE"]=str(temperature)
                
                except Exception as error:
                    self.mov.error(f"Cannot change the 'temperature', because {error}",parameters)
                    return
    
            if 'top_k' in parameters:
                try:
                
                    top_k=int(parameters['top_k'])
                    if top_k < 1:
                        
                        self.mov.error("Cannot set less than one tokens.",parameters)
                        return
                    
                    elif top_k > 100:
                        
                        self.mov.error("Cannot set more than one hundred tokens.",parameters)
                        return
                    
                    else:
                        
                        os.environ["REPLY_TOP_K"]=str(top_k)
                
                except Exception as error:
                    self.mov.error(f"Cannot change the 'top_k', because {error}",parameters)
                    return        
            
            if 'top_p' in parameters:
                try:
                
                    top_p=float(parameters['top_p'])
                    if top_p < 0.0:
                        
                        self.mov.error("Cannot set a top_p less than '0.0'.",parameters)
                        return
                    
                    elif top_p > 1.0:
                        
                        self.mov.error("Cannot set a top_p higher than '1.0'.",parameters)
                        return
                    
                    else:

                        os.environ["REPLY_TOP_P"]=str(top_p)
                
                except Exception as error:
                    self.mov.error(f"Cannot change the 'top_p', because {error}",parameters)
                    return
                
            if 'system_prompt' in parameters:

                system_prompt=str(parameters['system_prompt'])
                system_prompt_len=len(system_prompt)
                if system_prompt_len < 10:
                        
                    self.mov.error("Cannot set a 'system_prompt' with less than 10 characters.",parameters)
                    return
                    
                elif system_prompt_len > 10000:
                        
                    self.mov.error("Cannot set a 'system_prompt' with more than 10 thousand characters.",parameters)
                    return
                    
                else:

                    os.environ["REPLY_SYSTEM_PROMPT"]=system_prompt               
                    
            
            self.mov.info("Changed the component parameters",parameters)
            
            
        except Exception:
            
            logging.exception(f"Unexpected message {body}")
